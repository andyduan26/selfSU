from django.urls import path

from .views import (
    HealthCheckAPIView,
    LessonPlayAPIView,
    PublicCourseDetailAPIView,
    PublicCourseListAPIView,
    PublicTeacherDetailAPIView,
    R2PresignedUploadAPIView,
    TeacherApplicationAPIView,
    TeacherCourseDetailAPIView,
    TeacherCourseListCreateAPIView,
    TeacherStatusAPIView,
)


urlpatterns = [
    path('health/', HealthCheckAPIView.as_view(), name='health-check'),
    path('courses/', PublicCourseListAPIView.as_view(), name='public-course-list'),
    path('courses/<int:pk>/', PublicCourseDetailAPIView.as_view(), name='public-course-detail'),
    path('teachers/<int:pk>/', PublicTeacherDetailAPIView.as_view(), name='public-teacher-detail'),
    path('lessons/<int:pk>/play/', LessonPlayAPIView.as_view(), name='lesson-play'),
    path('uploads/r2/presign/', R2PresignedUploadAPIView.as_view(), name='r2-presigned-upload'),
    path('teacher/applications/', TeacherApplicationAPIView.as_view(), name='teacher-application'),
    path('teacher/courses/', TeacherCourseListCreateAPIView.as_view(), name='teacher-course-list-create'),
    path('teacher/courses/<int:pk>/', TeacherCourseDetailAPIView.as_view(), name='teacher-course-detail'),
    path('teacher/status/', TeacherStatusAPIView.as_view(), name='teacher-status'),
]
