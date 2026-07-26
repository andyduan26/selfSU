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
