from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from import_export.admin import ExportMixin

from .models import User


@admin.register(User)
class UserAdmin(ExportMixin, DjangoUserAdmin):
    list_display = ['id', 'username', 'nickname', 'email', 'phone', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['is_staff', 'is_active', 'date_joined']
    search_fields = ['username', 'nickname', 'email', 'phone']
    ordering = ['-date_joined']
    list_per_page = 20
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('个人资料', {'fields': ('nickname', 'phone')}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ('个人资料', {'fields': ('nickname', 'email', 'phone')}),
    )

# Register your models here.
