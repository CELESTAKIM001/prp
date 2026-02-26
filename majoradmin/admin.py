from django.contrib import admin
from .models import AdminLog, County, Task, SiteContent, DatabaseClearLog, UserSession


@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'user', 'description', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['user__username', 'description']
    readonly_fields = ['timestamp']


@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'code']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'assigned_to', 'status', 'priority', 'created_at']
    list_filter = ['status', 'priority']
    search_fields = ['title', 'assigned_to__username']


@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'content_type', 'is_active', 'order', 'created_at']
    list_filter = ['content_type', 'is_active']
    search_fields = ['title', 'content']


@admin.register(DatabaseClearLog)
class DatabaseClearLogAdmin(admin.ModelAdmin):
    list_display = ['cleared_by', 'cleared_at', 'tables_cleared']
    readonly_fields = ['cleared_at']


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'login_time', 'logout_time', 'is_active']
    list_filter = ['is_active']
    search_fields = ['user__username']
