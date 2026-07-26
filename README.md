# 东方知识库

知识分享/视频课程平台，面向普通用户、认证教师和管理员。

## 技术栈

- Backend: Django 4.2 LTS, Django REST Framework, SimpleUI Admin
- Frontend: Vue3, Vite, Vue Router, Pinia, Axios
- Dev DB: SQLite
- Production: PostgreSQL, Railway, Vercel, Cloudflare R2

## 本地启动

```bash
cd backend
source ../.venv/bin/activate
python manage.py migrate
python manage.py runserver
```

```bash
cd frontend
npm install
npm run dev
```
