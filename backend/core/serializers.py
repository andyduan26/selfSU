from rest_framework import serializers

from accounts.serializers import UserProfileSerializer
from .models import (
    Comment,
    Course,
    CourseChapter,
    CourseLesson,
    Favorite,
    Income,
    Order,
    TeacherApplication,
    TeacherProfile,
    Withdraw,
)


class TeacherApplicationSerializer(serializers.ModelSerializer):
    notice = serializers.SerializerMethodField()

    class Meta:
        model = TeacherApplication
        fields = '__all__'
        read_only_fields = ['id', 'user', 'status', 'review_note', 'created_at', 'updated_at', 'notice']

    def get_notice(self, obj):
        if obj.status == TeacherApplication.STATUS_PENDING:
            return '耐心等待2-3个工作日，结果会邮箱通知。'
        return ''


class TeacherProfileSerializer(serializers.ModelSerializer):
    user_detail = UserProfileSerializer(source='user', read_only=True)

    class Meta:
        model = TeacherProfile
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class CourseLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseLesson
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class CourseChapterSerializer(serializers.ModelSerializer):
    lessons = CourseLessonSerializer(many=True, read_only=True)

    class Meta:
        model = CourseChapter
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class CourseSerializer(serializers.ModelSerializer):
    chapters = CourseChapterSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'view_count']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class WithdrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdraw
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
