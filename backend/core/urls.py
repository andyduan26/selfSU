from django.urls import path

from .views import HealthCheckAPIView, TeacherApplicationAPIView, TeacherStatusAPIView


urlpatterns = [
    path('health/', HealthCheckAPIView.as_view(), name='health-check'),
    path('teacher/applications/', TeacherApplicationAPIView.as_view(), name='teacher-application'),
    path('teacher/status/', TeacherStatusAPIView.as_view(), name='teacher-status'),
]
