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

## 用户注册

`POST /api/auth/register/`

请求：

```json
{
  "username": "student01",
  "nickname": "东方学员",
  "email": "student01@example.com",
  "phone": "13800138000",
  "password": "StrongPass123"
}
```

返回 `access`、`refresh` 和当前用户资料。

## 用户登录

`POST /api/auth/login/`

请求：

```json
{
  "username": "student01",
  "password": "StrongPass123"
}
```

返回 `access`、`refresh` 和当前用户资料。

## 当前用户

`GET /api/auth/me/`

请求头：

```http
Authorization: Bearer access-token
```

## 修改个人资料

`PUT /api/auth/me/`

请求：

```json
{
  "nickname": "新昵称",
  "email": "new@example.com",
  "phone": "13700137000"
}
```

`POST /api/auth/token/refresh/`

请求：

```json
{
  "refresh": "refresh-token"
}
```
