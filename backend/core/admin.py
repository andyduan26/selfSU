from django.contrib import admin
from import_export.admin import ExportMixin

admin.site.site_header = '东方知识库管理后台'
admin.site.site_title = '东方知识库'
admin.site.index_title = '管理中心'

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


class BaseAdmin(ExportMixin, admin.ModelAdmin):
    list_per_page = 20


@admin.register(TeacherApplication)
class TeacherApplicationAdmin(BaseAdmin):
    list_display = ['id', 'user', 'real_name', 'phone', 'email', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'user__nickname', 'real_name', 'phone', 'email']
    ordering = ['-created_at']
    actions = ['approve_applications', 'reject_applications']

    @admin.action(description='审核通过所选教师申请')
    def approve_applications(self, request, queryset):
        for application in queryset:
            application.approve('管理员审核通过')
        self.message_user(request, f'已通过 {queryset.count()} 条教师认证申请')

    @admin.action(description='拒绝所选教师申请')
    def reject_applications(self, request, queryset):
        for application in queryset:
            application.reject('管理员审核拒绝')
        self.message_user(request, f'已拒绝 {queryset.count()} 条教师认证申请')


@admin.register(TeacherProfile)
class TeacherProfileAdmin(BaseAdmin):
    list_display = ['id', 'user', 'display_name', 'title', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'user__nickname', 'display_name', 'title']
    ordering = ['-created_at']


@admin.register(Course)
class CourseAdmin(BaseAdmin):
    list_display = ['id', 'title', 'teacher', 'category', 'price', 'audit_status', 'publish_status', 'has_trial', 'sort_weight', 'view_count']
    list_filter = ['audit_status', 'publish_status', 'has_trial', 'category', 'created_at']
    search_fields = ['title', 'summary', 'category', 'teacher__display_name', 'teacher__user__username']
    ordering = ['-sort_weight', '-created_at']


@admin.register(CourseChapter)
class CourseChapterAdmin(BaseAdmin):
    list_display = ['id', 'course', 'title', 'sort_order', 'created_at']
    list_filter = ['created_at']
    search_fields = ['course__title', 'title', 'summary']
    ordering = ['course', 'sort_order', 'id']


@admin.register(CourseLesson)
class CourseLessonAdmin(BaseAdmin):
    list_display = ['id', 'chapter', 'title', 'is_trial', 'duration_seconds', 'sort_order', 'created_at']
    list_filter = ['is_trial', 'created_at']
    search_fields = ['chapter__course__title', 'chapter__title', 'title']
    ordering = ['chapter', 'sort_order', 'id']


@admin.register(Order)
class OrderAdmin(BaseAdmin):
    list_display = ['id', 'order_no', 'user', 'course', 'amount', 'pay_status', 'payment_method', 'paid_at', 'created_at']
    list_filter = ['pay_status', 'payment_method', 'paid_at', 'created_at']
    search_fields = ['order_no', 'user__username', 'user__nickname', 'course__title']
    ordering = ['-created_at']


@admin.register(Income)
class IncomeAdmin(BaseAdmin):
    list_display = ['id', 'teacher', 'course', 'order', 'gross_amount', 'platform_amount', 'teacher_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['teacher__display_name', 'course__title', 'order__order_no']
    ordering = ['-created_at']


@admin.register(Withdraw)
class WithdrawAdmin(BaseAdmin):
    list_display = ['id', 'teacher', 'amount', 'account_name', 'status', 'paid_at', 'created_at']
    list_filter = ['status', 'paid_at', 'created_at']
    search_fields = ['teacher__display_name', 'teacher__user__username', 'account_name', 'account_no']
    ordering = ['-created_at']


@admin.register(Comment)
class CommentAdmin(BaseAdmin):
    list_display = ['id', 'user', 'course', 'lesson', 'rating', 'is_visible', 'created_at']
    list_filter = ['is_visible', 'rating', 'created_at']
    search_fields = ['user__username', 'user__nickname', 'course__title', 'lesson__title', 'content']
    ordering = ['-created_at']


@admin.register(Favorite)
class FavoriteAdmin(BaseAdmin):
    list_display = ['id', 'user', 'course', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__nickname', 'course__title']
    ordering = ['-created_at']

# Register your models here.
