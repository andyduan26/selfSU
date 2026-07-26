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

`POST /api/auth/token/refresh/`

请求：

```json
{
  "refresh": "refresh-token"
}
```
