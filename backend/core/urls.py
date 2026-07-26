from django.urls import path

from .views import (
    HealthCheckAPIView,
    PublicCourseListAPIView,
    TeacherApplicationAPIView,
    TeacherCourseDetailAPIView,
    TeacherCourseListCreateAPIView,
    TeacherStatusAPIView,
)


urlpatterns = [
    path('health/', HealthCheckAPIView.as_view(), name='health-check'),
    path('courses/', PublicCourseListAPIView.as_view(), name='public-course-list'),
    path('teacher/applications/', TeacherApplicationAPIView.as_view(), name='teacher-application'),
    path('teacher/courses/', TeacherCourseListCreateAPIView.as_view(), name='teacher-course-list-create'),
    path('teacher/courses/<int:pk>/', TeacherCourseDetailAPIView.as_view(), name='teacher-course-detail'),
    path('teacher/status/', TeacherStatusAPIView.as_view(), name='teacher-status'),
]
