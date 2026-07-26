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


class PublicTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherProfile
        fields = ['id', 'display_name', 'title', 'bio', 'avatar', 'created_at']


class CourseLessonSerializer(serializers.ModelSerializer):
    can_play = serializers.SerializerMethodField()

    class Meta:
        model = CourseLesson
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_can_play(self, obj):
        request = self.context.get('request')
        if obj.is_trial:
            return True
        if not request or not request.user.is_authenticated:
            return False
        return Order.objects.filter(
            user=request.user,
            course=obj.chapter.course,
            pay_status=Order.PAY_PAID,
        ).exists()


class CourseChapterSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField()

    class Meta:
        model = CourseChapter
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_lessons(self, obj):
        return CourseLessonSerializer(obj.lessons.all(), many=True, context=self.context).data


class CourseSerializer(serializers.ModelSerializer):
    chapters = serializers.SerializerMethodField()
    teacher = PublicTeacherSerializer(read_only=True)

    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'view_count']

    def get_chapters(self, obj):
        return CourseChapterSerializer(obj.chapters.all(), many=True, context=self.context).data


class TeacherCourseLessonInputSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = CourseLesson
        fields = ['id', 'title', 'video_file', 'is_trial', 'sort_order']


class TeacherCourseChapterInputSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    lessons = TeacherCourseLessonInputSerializer(many=True, required=False)

    class Meta:
        model = CourseChapter
        fields = ['id', 'title', 'summary', 'sort_order', 'lessons']


class TeacherCourseSerializer(serializers.ModelSerializer):
    chapters = TeacherCourseChapterInputSerializer(many=True, required=False)

    class Meta:
        model = Course
        fields = [
            'id',
            'cover',
            'title',
            'category',
            'price',
            'summary',
            'suitable_audience',
            'audit_status',
            'audit_reject_reason',
            'publish_status',
            'has_trial',
            'sort_weight',
            'view_count',
            'chapters',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'audit_status',
            'audit_reject_reason',
            'publish_status',
            'has_trial',
            'sort_weight',
            'view_count',
            'created_at',
            'updated_at',
        ]

    def create(self, validated_data):
        chapters_data = validated_data.pop('chapters', [])
        course = Course.objects.create(
            teacher=self.context['teacher'],
            audit_status=Course.AUDIT_PENDING,
            publish_status=Course.PUBLISH_DRAFT,
            **validated_data,
        )
        self.sync_chapters(course, chapters_data)
        return course

    def update(self, instance, validated_data):
        chapters_data = validated_data.pop('chapters', None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.audit_status = Course.AUDIT_PENDING
        instance.publish_status = Course.PUBLISH_DRAFT
        instance.audit_reject_reason = ''
        instance.save()
        if chapters_data is not None:
            instance.chapters.all().delete()
            self.sync_chapters(instance, chapters_data)
        return instance

    def sync_chapters(self, course, chapters_data):
        has_trial = False
        for chapter_data in chapters_data:
            lessons_data = chapter_data.pop('lessons', [])
            chapter_data.pop('id', None)
            chapter = CourseChapter.objects.create(course=course, **chapter_data)
            for lesson_data in lessons_data:
                lesson_data.pop('id', None)
                lesson = CourseLesson.objects.create(chapter=chapter, **lesson_data)
                has_trial = has_trial or lesson.is_trial
        if has_trial != course.has_trial:
            course.has_trial = has_trial
            course.save(update_fields=['has_trial', 'updated_at'])


class OrderSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_cover = serializers.CharField(source='course.cover', read_only=True)
    teacher_name = serializers.CharField(source='course.teacher.display_name', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'order_no',
            'user',
            'course',
            'course_title',
            'course_cover',
            'teacher_name',
            'amount',
            'pay_status',
            'payment_method',
            'paid_at',
            'created_at',
            'updated_at',
        ]
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
        read_only_fields = ['id', 'teacher', 'status', 'review_note', 'paid_at', 'created_at', 'updated_at']


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
