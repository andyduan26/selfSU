import uuid
from pathlib import Path

import boto3
from django.conf import settings


class R2ConfigurationError(Exception):
    pass


def create_r2_presigned_upload(filename, content_type, folder):
    required_settings = [
        settings.R2_ACCOUNT_ID,
        settings.R2_ACCESS_KEY_ID,
        settings.R2_SECRET_ACCESS_KEY,
        settings.R2_BUCKET_NAME,
        settings.R2_PUBLIC_BASE_URL,
    ]
    if not all(required_settings):
        raise R2ConfigurationError('Cloudflare R2 环境变量未配置完整')

    suffix = Path(filename).suffix
    object_key = f'{folder.strip("/")}/{uuid.uuid4().hex}{suffix}'
    endpoint_url = f'https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com'
    client = boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        region_name='auto',
    )
    upload_url = client.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': settings.R2_BUCKET_NAME,
            'Key': object_key,
            'ContentType': content_type,
        },
        ExpiresIn=settings.R2_UPLOAD_URL_EXPIRES,
    )
    return {
        'upload_url': upload_url,
        'public_url': f'{settings.R2_PUBLIC_BASE_URL.rstrip("/")}/{object_key}',
        'object_key': object_key,
    }
