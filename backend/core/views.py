from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import TeacherApplication
from .serializers import TeacherApplicationSerializer, TeacherProfileSerializer


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

# Create your views here.
