from django.urls import path
from . import views
from apartments.views import create_notification

urlpatterns = [
    # Login/Logout
    path('login/', views.major_admin_login, name='majoradmin_login'),
    path('logout/', views.major_admin_logout, name='majoradmin_logout'),
    
    # Dashboard
    path('', views.majoradmin_dashboard, name='majoradmin_dashboard'),
    
    # Notifications
    path('notifications/create/', create_notification, name='majoradmin_create_notification'),
    
    # Admin Logs
    path('logs/', views.admin_logs, name='majoradmin_logs'),
    
    # User Management
    path('users/', views.user_management, name='majoradmin_users'),
    path('users/edit/<int:user_id>/', views.edit_user, name='majoradmin_edit_user'),
    path('users/password/<int:user_id>/', views.change_user_password, name='majoradmin_change_password'),
    path('users/delete/<int:user_id>/', views.delete_user, name='majoradmin_delete_user'),
    
    # Task Management
    path('tasks/', views.task_management, name='majoradmin_tasks'),
    path('tasks/create/', views.create_task, name='majoradmin_create_task'),
    path('tasks/edit/<int:task_id>/', views.edit_task, name='majoradmin_edit_task'),
    path('tasks/delete/<int:task_id>/', views.delete_task, name='majoradmin_delete_task'),
    path('tasks/verify/<int:task_id>/', views.verify_task, name='majoradmin_verify_task'),
    
    # Site Content
    path('content/', views.site_content, name='majoradmin_site_content'),
    path('content/create/', views.create_content, name='majoradmin_create_content'),
    path('content/edit/<int:content_id>/', views.edit_content, name='majoradmin_edit_content'),
    path('content/delete/<int:content_id>/', views.delete_content, name='majoradmin_delete_content'),
    
    # County Management
    path('counties/', views.county_management, name='majoradmin_counties'),
    path('counties/create/', views.create_county, name='majoradmin_create_county'),
    path('counties/edit/<int:county_id>/', views.edit_county, name='majoradmin_edit_county'),
    path('counties/delete/<int:county_id>/', views.delete_county, name='majoradmin_delete_county'),
    
    # User Sessions
    path('sessions/', views.user_sessions, name='majoradmin_sessions'),
    
    # Database Management
    path('database/', views.database_management, name='majoradmin_database'),
    path('database/clear/', views.clear_database, name='majoradmin_clear_database'),
]
