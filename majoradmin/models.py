from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class AdminLog(models.Model):
    """Model for logging all admin actions"""
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('TASK_ASSIGNED', 'Task Assigned'),
        ('TASK_COMPLETED', 'Task Completed'),
        ('TASK_VERIFIED', 'Task Verified'),
        ('USER_EDITED', 'User Edited'),
        ('USER_PASSWORD_CHANGED', 'Password Changed'),
        ('USER_DELETED', 'User Deleted'),
        ('CONTENT_UPDATED', 'Content Updated'),
        ('DATABASE_CLEARED', 'Database Cleared'),
    ]
    
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_logs')
    description = models.TextField()
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    related_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='affected_by_admin')
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Admin Logs'
    
    def __str__(self):
        return f"{self.action} by {self.user} at {self.timestamp}"


class County(models.Model):
    """Model for counties - used in dropdown"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Counties'
    
    def __str__(self):
        return self.name


class Task(models.Model):
    """Model for assigning tasks to users"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('VERIFIED', 'Verified'),
        ('REJECTED', 'Rejected'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    priority = models.CharField(max_length=20, default='NORMAL')
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_tasks')
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.assigned_to}"


class SiteContent(models.Model):
    """Model for managing site content - text, videos, etc"""
    CONTENT_TYPE_CHOICES = [
        ('TEXT', 'Text Content'),
        ('YOUTUBE', 'YouTube Video'),
        ('ANNOUNCEMENT', 'Announcement'),
        ('SECTION', 'Page Section'),
        ('BANNER', 'Banner'),
        ('FAQ', 'FAQ'),
    ]
    
    title = models.CharField(max_length=200)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES)
    content = models.TextField()
    youtube_url = models.URLField(blank=True, null=True)
    youtube_embed_code = models.TextField(blank=True, help_text="Custom YouTube embed code for responsive videos")
    section_key = models.CharField(max_length=100, blank=True, help_text="Unique key for page sections")
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name_plural = 'Site Contents'
    
    def __str__(self):
        return f"{self.title} ({self.content_type})"
    
    def get_youtube_embed_url(self):
        """Extract YouTube video ID and return embed URL"""
        if self.youtube_url:
            # Extract video ID from various YouTube URL formats
            import re
            patterns = [
                r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
            ]
            for pattern in patterns:
                match = re.search(pattern, self.youtube_url)
                if match:
                    video_id = match.group(1)
                    return f"https://www.youtube.com/embed/{video_id}"
        return None


class DatabaseClearLog(models.Model):
    """Model for tracking database clears while preserving history"""
    cleared_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tables_cleared = models.JSONField(default=list)
    records_preserved = models.JSONField(default=dict, help_text="Count of records preserved in each table")
    cleared_at = models.DateTimeField(default=timezone.now)
    reason = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-cleared_at']
        verbose_name_plural = 'Database Clear Logs'
    
    def __str__(self):
        return f"Database cleared by {self.cleared_by} at {self.cleared_at}"


class UserSession(models.Model):
    """Model for tracking user login sessions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    login_time = models.DateTimeField(default=timezone.now)
    logout_time = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-login_time']
    
    def __str__(self):
        return f"{self.user} - {self.login_time}"
    
    def get_duration(self):
        """Calculate session duration"""
        if self.logout_time:
            return self.logout_time - self.login_time
        elif self.is_active:
            return timezone.now() - self.login_time
        return None
