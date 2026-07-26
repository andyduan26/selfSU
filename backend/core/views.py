from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import Course, TeacherApplication
from .serializers import CourseSerializer, TeacherApplicationSerializer, TeacherCourseSerializer, TeacherProfileSerializer


class HealthCheckAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({
            'code': 0,
            'message': 'success',
            'data': {
                'service': '东方知识库 API',
                'status': 'ok',
            },
        })


class TeacherApplicationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TeacherApplicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application = serializer.save(user=request.user)
        return Response({
            'code': 0,
            'message': 'success',
            'data': TeacherApplicationSerializer(application).data,
        }, status=201)


class TeacherStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = getattr(request.user, 'teacher_profile', None)
        application = request.user.teacher_applications.order_by('-created_at').first()
        return Response({
            'code': 0,
            'message': 'success',
            'data': {
                'is_teacher': bool(profile and profile.is_active),
                'application_status': application.status if application else '',
                'application': TeacherApplicationSerializer(application).data if application else None,
                'teacher_profile': TeacherProfileSerializer(profile).data if profile else None,
            },
        })


class TeacherCourseListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_teacher(self, request):
        teacher = getattr(request.user, 'teacher_profile', None)
        if not teacher or not teacher.is_active:
            return None
        return teacher

    def get(self, request):
        teacher = self.get_teacher(request)
        if not teacher:
            return Response({'code': 403, 'message': '请先申请认证教师', 'data': None}, status=403)
        courses = teacher.courses.prefetch_related('chapters__lessons').all()
        return Response({'code': 0, 'message': 'success', 'data': TeacherCourseSerializer(courses, many=True).data})

    def post(self, request):
        teacher = self.get_teacher(request)
        if not teacher:
            return Response({'code': 403, 'message': '请先申请认证教师', 'data': None}, status=403)
        serializer = TeacherCourseSerializer(data=request.data, context={'teacher': teacher})
        serializer.is_valid(raise_exception=True)
        course = serializer.save()
        return Response({'code': 0, 'message': 'success', 'data': TeacherCourseSerializer(course).data}, status=201)


class TeacherCourseDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_teacher(self, request):
        teacher = getattr(request.user, 'teacher_profile', None)
        if not teacher or not teacher.is_active:
            return None
        return teacher

    def get_course(self, request, pk):
        teacher = self.get_teacher(request)
        if not teacher:
            return None
        return get_object_or_404(Course.objects.prefetch_related('chapters__lessons'), pk=pk, teacher=teacher)

    def get(self, request, pk):
        course = self.get_course(request, pk)
        if course is None:
            return Response({'code': 403, 'message': '请先申请认证教师', 'data': None}, status=403)
        return Response({'code': 0, 'message': 'success', 'data': TeacherCourseSerializer(course).data})

    def put(self, request, pk):
        course = self.get_course(request, pk)
        if course is None:
            return Response({'code': 403, 'message': '请先申请认证教师', 'data': None}, status=403)
        serializer = TeacherCourseSerializer(course, data=request.data, context={'teacher': course.teacher})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'code': 0, 'message': 'success', 'data': serializer.data})

    def delete(self, request, pk):
        course = self.get_course(request, pk)
        if course is None:
            return Response({'code': 403, 'message': '请先申请认证教师', 'data': None}, status=403)
        course.delete()
        return Response(status=204)


class PublicCourseListAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        courses = Course.objects.filter(
            audit_status=Course.AUDIT_APPROVED,
            publish_status=Course.PUBLISH_PUBLISHED,
        ).prefetch_related('chapters__lessons')
        return Response({'code': 0, 'message': 'success', 'data': CourseSerializer(courses, many=True).data})

# Create your views here.
