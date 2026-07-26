# 安装说明

## 后端

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cd backend
python manage.py migrate
python manage.py runserver
```

## 前端

```bash
cd frontend
npm install
npm run dev
```

## Cloudflare R2

后端需要配置：

```bash
export R2_ACCOUNT_ID="your-account-id"
export R2_ACCESS_KEY_ID="your-access-key"
export R2_SECRET_ACCESS_KEY="your-secret-key"
export R2_BUCKET_NAME="your-bucket"
export R2_PUBLIC_BASE_URL="https://your-public-domain"
export R2_UPLOAD_URL_EXPIRES=3600
```

前端上传大文件时会先请求 `/api/uploads/r2/presign/`，再直接 PUT 到 R2，不经过 Django 文件流。

## 支付宝

后端需要在本地、Railway 或其他部署环境中配置以下变量。私钥和公钥只允许放在环境变量中，不能写入代码或提交到仓库。

```bash
export ALIPAY_APP_ID="your-app-id"
export ALIPAY_APP_PRIVATE_KEY="your-private-key"
export ALIPAY_PUBLIC_KEY="your-alipay-public-key"
export ALIPAY_GATEWAY_URL="https://openapi.alipay.com/gateway.do"
export ALIPAY_NOTIFY_URL="https://your-api-domain.com/api/alipay/notify/"
```

前端点击支付宝支付后会请求 `/api/orders/{order_no}/alipay/precreate/` 获取 `qr_code`，再每 3 秒请求 `/api/orders/{order_no}/status/` 查询支付结果。
