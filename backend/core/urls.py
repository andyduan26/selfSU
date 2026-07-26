from django.urls import path

from .views import (
    HealthCheckAPIView,
    CourseOrderCreateAPIView,
    LessonPlayAPIView,
    MyOrderListAPIView,
    PublicCourseDetailAPIView,
    PublicCourseListAPIView,
    PublicTeacherDetailAPIView,
    R2PresignedUploadAPIView,
    TeacherApplicationAPIView,
    TeacherCourseDetailAPIView,
    TeacherCourseListCreateAPIView,
    TeacherOrderListAPIView,
    TeacherStatusAPIView,
)


urlpatterns = [
    path('health/', HealthCheckAPIView.as_view(), name='health-check'),
    path('courses/', PublicCourseListAPIView.as_view(), name='public-course-list'),
    path('courses/<int:pk>/', PublicCourseDetailAPIView.as_view(), name='public-course-detail'),
    path('courses/<int:pk>/orders/', CourseOrderCreateAPIView.as_view(), name='course-order-create'),
    path('orders/', MyOrderListAPIView.as_view(), name='my-order-list'),
    path('teachers/<int:pk>/', PublicTeacherDetailAPIView.as_view(), name='public-teacher-detail'),
    path('lessons/<int:pk>/play/', LessonPlayAPIView.as_view(), name='lesson-play'),
    path('uploads/r2/presign/', R2PresignedUploadAPIView.as_view(), name='r2-presigned-upload'),
    path('teacher/applications/', TeacherApplicationAPIView.as_view(), name='teacher-application'),
    path('teacher/courses/', TeacherCourseListCreateAPIView.as_view(), name='teacher-course-list-create'),
    path('teacher/courses/<int:pk>/', TeacherCourseDetailAPIView.as_view(), name='teacher-course-detail'),
    path('teacher/orders/', TeacherOrderListAPIView.as_view(), name='teacher-order-list'),
    path('teacher/status/', TeacherStatusAPIView.as_view(), name='teacher-status'),
]
