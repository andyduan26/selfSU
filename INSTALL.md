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
