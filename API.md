# API

## 统一返回格式

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

## 健康检查

`GET /api/health/`

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "service": "东方知识库 API",
    "status": "ok"
  }
}
```

## JWT

`POST /api/auth/token/`

请求：

```json
{
  "username": "admin",
  "password": "your-password"
}
```

`POST /api/auth/token/refresh/`

请求：

```json
{
  "refresh": "refresh-token"
}
```
