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

## 核心模型 Serializer

当前阶段已建立以下后端基础 Serializer，供后续 APIView 增量接入：

- `TeacherApplicationSerializer`
- `TeacherProfileSerializer`
- `CourseSerializer`
- `CourseChapterSerializer`
- `CourseLessonSerializer`
- `OrderSerializer`
- `IncomeSerializer`
- `WithdrawSerializer`
- `CommentSerializer`
- `FavoriteSerializer`

## 教师认证申请

`POST /api/teacher/applications/`

请求头：

```http
Authorization: Bearer access-token
```

请求：

```json
{
  "real_name": "张老师",
  "phone": "13800138000",
  "email": "teacher@example.com",
  "bio": "教学经验说明"
}
```

返回待审核状态和提示文案：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "status": "pending",
    "notice": "耐心等待2-3个工作日，结果会邮箱通知。"
  }
}
```

## 教师认证状态

`GET /api/teacher/status/`

返回：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "is_teacher": false,
    "application_status": "pending",
    "application": {},
    "teacher_profile": null
  }
}
```

## 教师课程作品

`GET /api/teacher/courses/`

查询当前认证教师自己的课程作品。

`POST /api/teacher/courses/`

创建课程作品，创建后默认：

- `audit_status`: `pending`
- `publish_status`: `draft`

请求：

```json
{
  "title": "东方器物课",
  "cover": "r2://covers/course.jpg",
  "category": "美学",
  "price": "299.00",
  "summary": "课程简介",
  "suitable_audience": "设计师、品牌主理人",
  "chapters": [
    {
      "title": "第一章",
      "summary": "章节简介",
      "sort_order": 1,
      "lessons": [
        {
          "title": "试看导论",
          "video_file": "r2://videos/lesson.mp4",
          "is_trial": true,
          "sort_order": 1
        }
      ]
    }
  ]
}
```

`PUT /api/teacher/courses/{id}/`

编辑自己的课程作品，保存后重新进入待审核。

`DELETE /api/teacher/courses/{id}/`

删除自己的课程作品。

## 前台课程列表

`GET /api/courses/`

只返回管理员审核通过且已发布的课程。

支持按分类筛选：

`GET /api/courses/?category=美学`

## 前台课程详情

`GET /api/courses/{id}/`

只允许访问管理员审核通过且已发布的课程。返回课程封面、价格、讲师和章节目录；目录小节包含 `can_play`，用于判断当前用户是否可播放。

## 教师主页

`GET /api/teachers/{id}/`

返回教师公开资料，以及该教师审核通过且已发布的课程。

## 视频播放

`GET /api/lessons/{id}/play/`

- 试看小节：未登录也可播放
- 非试看小节：必须登录且已购买课程
- 未购买访问非试看小节返回 `403`
- 返回 `video_file`、`hls_url`、`duration`、`resolution`、`transcode_status`

## Cloudflare R2 预签名上传

`POST /api/uploads/r2/presign/`

仅认证教师可调用。后端返回 R2 预签名 PUT 地址，前端直接把封面/视频上传到 R2，数据库保存 `public_url`。

请求：

```json
{
  "filename": "lesson.mp4",
  "content_type": "video/mp4",
  "folder": "course-videos"
}
```

返回：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "upload_url": "https://...",
    "public_url": "https://cdn.example.com/course-videos/xxx.mp4",
    "object_key": "course-videos/xxx.mp4"
  }
}
```

## 创建课程订单

`POST /api/courses/{id}/orders/`

请求头：

```http
Authorization: Bearer access-token
```

请求：

```json
{
  "payment_method": "alipay"
}
```

规则：

- 免费课程直接创建 `paid` 订单并开通完整学习权限
- 付费课程创建 `pending` 订单
- 已支付订单可播放完整课程
- 未支付订单只能试看

## 我的订单

`GET /api/orders/`

返回当前用户自己的订单列表。

## 教师课程订单

`GET /api/teacher/orders/`

仅认证教师可访问，返回自己课程产生的订单数据。

## 支付宝扫码预下单

`POST /api/orders/{order_no}/alipay/precreate/`

请求头：

```http
Authorization: Bearer access-token
```

返回 `qr_code`，前端用 `qrcode` 生成二维码图片。支付宝密钥只从后端环境变量读取。

## 订单状态轮询

`GET /api/orders/{order_no}/status/`

请求头：

```http
Authorization: Bearer access-token
```

前端每 3 秒轮询一次；订单变为 `paid` 后跳转学习页，`closed` 或 `refunded` 时显示支付失败提示。

## 支付宝异步通知

`POST /api/alipay/notify/`

支付宝服务器回调地址。后端验签通过且 `trade_status` 为 `TRADE_SUCCESS` 或 `TRADE_FINISHED` 时，将订单标记为已支付。

返回支付宝要求的纯文本：`success` 或 `failure`。

`POST /api/auth/token/refresh/`

请求：

```json
{
  "refresh": "refresh-token"
}
```
