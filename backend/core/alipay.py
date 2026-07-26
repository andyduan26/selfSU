import base64
import json
from datetime import datetime

import requests
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from django.conf import settings


class AlipayConfigurationError(Exception):
    pass


class AlipayAPIError(Exception):
    pass


def _load_private_key(private_key):
    key_text = private_key.replace('\\n', '\n')
    if 'BEGIN' not in key_text:
        key_text = f'-----BEGIN PRIVATE KEY-----\n{key_text}\n-----END PRIVATE KEY-----'
    return serialization.load_pem_private_key(key_text.encode(), password=None)


def _load_public_key(public_key):
    key_text = public_key.replace('\\n', '\n')
    if 'BEGIN' not in key_text:
        key_text = f'-----BEGIN PUBLIC KEY-----\n{key_text}\n-----END PUBLIC KEY-----'
    return serialization.load_pem_public_key(key_text.encode())


def _build_sign_content(params):
    return '&'.join(
        f'{key}={params[key]}'
        for key in sorted(params)
        if key not in ['sign', 'sign_type'] and params[key] not in ['', None]
    )


def _sign(params):
    private_key = _load_private_key(settings.ALIPAY_APP_PRIVATE_KEY)
    content = _build_sign_content(params)
    signature = private_key.sign(content.encode(), padding.PKCS1v15(), hashes.SHA256())
    return base64.b64encode(signature).decode()


def create_alipay_precreate(order):
    if not all([settings.ALIPAY_APP_ID, settings.ALIPAY_APP_PRIVATE_KEY, settings.ALIPAY_GATEWAY_URL]):
        raise AlipayConfigurationError('支付宝环境变量未配置完整')

    biz_content = {
        'out_trade_no': order.order_no,
        'total_amount': str(order.amount),
        'subject': order.course.title,
    }
    params = {
        'app_id': settings.ALIPAY_APP_ID,
        'method': 'alipay.trade.precreate',
        'format': 'JSON',
        'charset': 'utf-8',
        'sign_type': 'RSA2',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'version': '1.0',
        'notify_url': settings.ALIPAY_NOTIFY_URL,
        'biz_content': json.dumps(biz_content, ensure_ascii=False, separators=(',', ':')),
    }
    params['sign'] = _sign(params)
    response = requests.post(settings.ALIPAY_GATEWAY_URL, data=params, timeout=15)
    response.raise_for_status()
    payload = response.json()
    result = payload.get('alipay_trade_precreate_response', {})
    if result.get('code') != '10000':
        raise AlipayAPIError(result.get('sub_msg') or result.get('msg') or '支付宝预下单失败')
    return {
        'qr_code': result['qr_code'],
        'out_trade_no': result.get('out_trade_no', order.order_no),
    }


def verify_alipay_notify(params):
    if not settings.ALIPAY_PUBLIC_KEY:
        raise AlipayConfigurationError('支付宝环境变量未配置完整')
    signature = params.get('sign')
    if not signature:
        return False
    public_key = _load_public_key(settings.ALIPAY_PUBLIC_KEY)
    content = _build_sign_content(params)
    try:
        public_key.verify(
            base64.b64decode(signature),
            content.encode(),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
    except (InvalidSignature, ValueError):
        return False
    return True
