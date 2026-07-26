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
