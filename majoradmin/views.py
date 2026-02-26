from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta
import json

from .models import (
    AdminLog, County, Task, SiteContent, 
    DatabaseClearLog, UserSession
)


# Decorator to check if user is superuser
def major_admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('majoradmin_login')
        if not request.user.is_superuser:
            messages.error(request, 'Access denied. Superuser privileges required.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def major_admin_login(request):
    """Login view for major admin (not accessible from website)"""
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('majoradmin_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_superuser:
            login(request, user)
            
            # Log the login action
            AdminLog.objects.create(
                action='LOGIN',
                user=user,
                description=f'Superuser {username} logged in',
                ip_address=get_client_ip(request)
            )
            
            return redirect('majoradmin_dashboard')
        else:
            messages.error(request, 'Invalid credentials or not a superuser.')
    
    return render(request, 'majoradmin/login.html')


@major_admin_required
def major_admin_logout(request):
    """Logout from major admin"""
    AdminLog.objects.create(
        action='LOGOUT',
        user=request.user,
        description=f'Superuser {request.user.username} logged out',
        ip_address=get_client_ip(request)
    )
    logout(request)
    return redirect('majoradmin_login')


import json
from datetime import datetime, timedelta

@major_admin_required
def majoradmin_dashboard(request):
    """Main dashboard for major admin"""
    # Get statistics
    total_users = User.objects.count()
    active_sessions = UserSession.objects.filter(is_active=True).count()
    total_tasks = Task.objects.count()
    pending_tasks = Task.objects.filter(status='PENDING').count()
    completed_tasks = Task.objects.filter(status='COMPLETED').count()
    verified_tasks = Task.objects.filter(status='VERIFIED').count()
    total_logs = AdminLog.objects.count()
    site_contents = SiteContent.objects.count()
    counties = County.objects.count()
    
    # Recent logs
    recent_logs = AdminLog.objects.all()[:10]
    
    # Recent user sessions
    recent_sessions = UserSession.objects.order_by('-login_time')[:10]
    
    # Latest 10 users for sidebar dropdown
    latest_users = User.objects.order_by('-date_joined')[:10]
    
    # Latest 10 tasks for sidebar dropdown
    latest_tasks = Task.objects.order_by('-created_at')[:10]
    
    # Tasks by status
    tasks_by_status = Task.objects.values('status').annotate(count=Count('id'))
    
    # Calculate task counts
    in_progress_tasks = Task.objects.filter(status='IN_PROGRESS').count()
    
    # Get login data for chart (last 30 days)
    today = timezone.now().date()
    
    # Get login counts per day
    login_data = []
    for i in range(30):
        day = today - timedelta(days=29-i)
        
        # Count logins for this day
        login_count = UserSession.objects.filter(
            login_time__date=day
        ).count()
        
        login_data.append({
            'date': day.strftime('%Y-%m-%d'),
            'label': day.strftime('%b %d'),
            'count': login_count
        })
    
    # Convert to JSON for JavaScript
    login_data_json = json.dumps(login_data)
    
    context = {
        'total_users': total_users,
        'active_sessions': active_sessions,
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks,
        'verified_tasks': verified_tasks,
        'in_progress_tasks': in_progress_tasks,
        'total_logs': total_logs,
        'site_contents': site_contents,
        'counties': counties,
        'recent_logs': recent_logs,
        'recent_sessions': recent_sessions,
        'latest_users': latest_users,
        'latest_tasks': latest_tasks,
        'tasks_by_status': tasks_by_status,
        'login_data_json': login_data_json,
    }
    
    return render(request, 'majoradmin/dashboard.html', context)


# ========== Admin Logs ==========

@major_admin_required
def admin_logs(request):
    """View all admin logs"""
    logs = AdminLog.objects.all()
    
    # Filter by action
    action_filter = request.GET.get('action')
    if action_filter:
        logs = logs.filter(action=action_filter)
    
    # Filter by user
    user_filter = request.GET.get('user')
    if user_filter:
        logs = logs.filter(user__username__icontains=user_filter)
    
    # Filter by date range
    date_from = request.GET.get('date_from')
    if date_from:
        logs = logs.filter(timestamp__date__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        logs = logs.filter(timestamp__date__lte=date_to)
    
    logs = logs[:100]  # Limit to 100 most recent
    
    actions = AdminLog.ACTION_CHOICES
    
    context = {
        'logs': logs,
        'actions': actions,
    }
    
    return render(request, 'majoradmin/logs.html', context)


# ========== User Management ==========

@major_admin_required
def user_management(request):
    """Manage all users"""
    users = User.objects.select_related('profile').annotate(
        task_count=Count('assigned_tasks'),
        session_count=Count('sessions')
    )
    
    search = request.GET.get('search')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    # Get sort option
    sort = request.GET.get('sort', '-date_joined')
    if sort == 'username':
        users = users.order_by('username')
    elif sort == '-username':
        users = users.order_by('-username')
    elif sort == 'date_joined':
        users = users.order_by('date_joined')
    elif sort == '-date_joined':
        users = users.order_by('-date_joined')
    elif sort == 'last_login':
        users = users.order_by('last_login')
    elif sort == '-last_login':
        users = users.order_by('-last_login')
    else:
        users = users.order_by('-date_joined')
    
    # Get pagination limit
    limit = int(request.GET.get('limit', 10))
    if limit == 0:
        # Show all
        paginated_users = users
    else:
        paginated_users = users[:limit]
    
    # Calculate total count
    total_count = users.count()
    
    context = {
        'users': paginated_users,
        'total_count': total_count,
        'current_limit': limit,
        'current_sort': sort,
    }
    
    return render(request, 'majoradmin/users.html', context)


@major_admin_required
def edit_user(request, user_id):
    """Edit a user"""
    user = get_object_or_404(User, id=user_id)
    
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        
        is_active = request.POST.get('is_active')
        user.is_active = is_active == 'on'
        
        user.save()
        
        # Update profile role
        role = request.POST.get('role')
        if role:
            profile.role = role
        
        # Update permissions
        profile.can_add_tenants = request.POST.get('can_add_tenants') == 'on'
        profile.can_approve_payments = request.POST.get('can_approve_payments') == 'on'
        profile.can_view_reports = request.POST.get('can_view_reports') == 'on'
        profile.can_create_lease = request.POST.get('can_create_lease') == 'on'
        profile.can_create_payment = request.POST.get('can_create_payment') == 'on'
        profile.can_create_maintenance = request.POST.get('can_create_maintenance') == 'on'
        profile.can_manage_properties = request.POST.get('can_manage_properties') == 'on'
        profile.can_manage_apartments = request.POST.get('can_manage_apartments') == 'on'
        profile.can_manage_users = request.POST.get('can_manage_users') == 'on'
        profile.can_view_all_payments = request.POST.get('can_view_all_payments') == 'on'
        profile.can_view_all_maintenance = request.POST.get('can_view_all_maintenance') == 'on'
        
        # Update assigned property
        assigned_property_id = request.POST.get('assigned_property')
        if assigned_property_id:
            from apartments.models import Property
            try:
                profile.assigned_property = Property.objects.get(id=assigned_property_id)
            except Property.DoesNotExist:
                profile.assigned_property = None
        else:
            profile.assigned_property = None
        
        profile.save()
        
        # Log the action
        AdminLog.objects.create(
            action='USER_EDITED',
            user=request.user,
            description=f'Edited user {user.username}',
            details={'edited_fields': list(request.POST.keys())},
            related_user=user,
            ip_address=get_client_ip(request)
        )
        
        messages.success(request, f'User {user.username} updated successfully.')
        return redirect('majoradmin_users')
    
    # Get all properties for the dropdown
    from apartments.models import Property
    properties = Property.objects.all()
    
    context = {
        'edit_user': user,
        'profile': profile,
        'properties': properties,
    }
    
    return render(request, 'majoradmin/edit_user.html', context)


@major_admin_required
def change_user_password(request, user_id):
    """Change user password"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('majoradmin_change_password', user_id=user_id)
        
        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return redirect('majoradmin_change_password', user_id=user_id)
        
        user.password = make_password(new_password)
        user.save()
        
        # Log the action
        AdminLog.objects.create(
            action='USER_PASSWORD_CHANGED',
            user=request.user,
            description=f'Changed password for user {user.username}',
            related_user=user,
            ip_address=get_client_ip(request)
        )
        
        messages.success(request, f'Password for {user.username} changed successfully.')
        return redirect('majoradmin_users')
    
    context = {
        'change_password_user': user,
    }
    
    return render(request, 'majoradmin/change_password.html', context)


@major_admin_required
def delete_user(request, user_id):
    """Delete a user account"""
    user = get_object_or_404(User, id=user_id)
    
    if request.user.id == user.id:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('majoradmin_users')
    
    if request.method == 'POST':
        username = user.username
        
        # Log before deletion
        AdminLog.objects.create(
            action='USER_DELETED',
            user=request.user,
            description=f'Deleted user {username}',
            related_user=None,  # User is being deleted
            ip_address=get_client_ip(request)
        )
        
        user.delete()
        messages.success(request, f'User {username} deleted successfully.')
        return redirect('majoradmin_users')
    
    context = {
        'delete_user': user,
    }
    
    return render(request, 'majoradmin/delete_user.html', context)


# ========== Task Management ==========

@major_admin_required
def task_management(request):
    """Manage all tasks"""
    tasks = Task.objects.select_related('assigned_to', 'assigned_by').order_by('-created_at')
    
    status_filter = request.GET.get('status')
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    assigned_to_filter = request.GET.get('assigned_to')
    if assigned_to_filter:
        tasks = tasks.filter(assigned_to__id=assigned_to_filter)
    
    context = {
        'tasks': tasks,
        'users': User.objects.filter(is_active=True),
    }
    
    return render(request, 'majoradmin/tasks.html', context)


@major_admin_required
def create_task(request):
    """Create a new task"""
    if request.method == 'POST':
        task = Task(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            assigned_to_id=request.POST.get('assigned_to'),
            assigned_by=request.user,
            priority=request.POST.get('priority'),
            due_date=request.POST.get('due_date') or None,
        )
        task.save()
        
        # Log the action
        AdminLog.objects.create(
            action='TASK_ASSIGNED',
            user=request.user,
            description=f'Assigned task "{task.title}" to {task.assigned_to.username}',
            related_user=task.assigned_to,
            ip_address=get_client_ip(request)
        )
        
        messages.success(request, 'Task assigned successfully.')
        return redirect('majoradmin_tasks')
    
    context = {
        'users': User.objects.filter(is_active=True),
    }
    
    return render(request, 'majoradmin/create_task.html', context)


@major_admin_required
def edit_task(request, task_id):
    """Edit a task"""
    task = get_object_or_404(Task, id=task_id)
    
    if request.method == 'POST':
        task.title = request.POST.get('title')
        task.description = request.POST.get('description')
        task.assigned_to_id = request.POST.get('assigned_to')
        task.priority = request.POST.get('priority')
        task.due_date = request.POST.get('due_date') or None
        task.status = request.POST.get('status')
        task.notes = request.POST.get('notes')
        task.save()
        
        messages.success(request, 'Task updated successfully.')
        return redirect('majoradmin_tasks')
    
    context = {
        'task': task,
        'users': User.objects.filter(is_active=True),
    }
    
    return render(request, 'majoradmin/edit_task.html', context)


@major_admin_required
def delete_task(request, task_id):
    """Delete a task"""
    task = get_object_or_404(Task, id=task_id)
    
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully.')
        return redirect('majoradmin_tasks')
    
    context = {
        'task': task,
    }
    
    return render(request, 'majoradmin/delete_task.html', context)


@major_admin_required
def verify_task(request, task_id):
    """Verify a completed task"""
    task = get_object_or_404(Task, id=task_id)
    
    task.status = 'VERIFIED'
    task.verified_by = request.user
    task.verified_at = timezone.now()
    task.save()
    
    # Log the action
    AdminLog.objects.create(
        action='TASK_VERIFIED',
        user=request.user,
        description=f'Verified task "{task.title}"',
        related_user=task.assigned_to,
        ip_address=get_client_ip(request)
    )
    
    messages.success(request, 'Task verified successfully.')
    return redirect('majoradmin_tasks')


# ========== Site Content Management ==========

@major_admin_required
def site_content(request):
    """Manage site content"""
    contents = SiteContent.objects.all()
    
    content_type_filter = request.GET.get('content_type')
    if content_type_filter:
        contents = contents.filter(content_type=content_type_filter)
    
    context = {
        'contents': contents,
    }
    
    return render(request, 'majoradmin/site_content.html', context)


@major_admin_required
def create_content(request):
    """Create new site content"""
    if request.method == 'POST':
        content = SiteContent(
            title=request.POST.get('title'),
            content_type=request.POST.get('content_type'),
            content=request.POST.get('content'),
            youtube_url=request.POST.get('youtube_url') or None,
            section_key=request.POST.get('section_key') or None,
            is_active=request.POST.get('is_active') == 'on',
            order=request.POST.get('order') or 0,
            created_by=request.user,
        )
        content.save()
        
        # Log the action
        AdminLog.objects.create(
            action='CONTENT_UPDATED',
            user=request.user,
            description=f'Created content "{content.title}"',
            ip_address=get_client_ip(request)
        )
        
        messages.success(request, 'Content created successfully.')
        return redirect('majoradmin_site_content')
    
    return render(request, 'majoradmin/create_content.html')


@major_admin_required
def edit_content(request, content_id):
    """Edit site content"""
    content = get_object_or_404(SiteContent, id=content_id)
    
    if request.method == 'POST':
        content.title = request.POST.get('title')
        content.content_type = request.POST.get('content_type')
        content.content = request.POST.get('content')
        content.youtube_url = request.POST.get('youtube_url') or None
        content.section_key = request.POST.get('section_key') or None
        content.is_active = request.POST.get('is_active') == 'on'
        content.order = request.POST.get('order') or 0
        content.save()
        
        messages.success(request, 'Content updated successfully.')
        return redirect('majoradmin_site_content')
    
    context = {
        'content': content,
    }
    
    return render(request, 'majoradmin/edit_content.html', context)


@major_admin_required
def delete_content(request, content_id):
    """Delete site content"""
    content = get_object_or_404(SiteContent, id=content_id)
    
    if request.method == 'POST':
        content.delete()
        messages.success(request, 'Content deleted successfully.')
        return redirect('majoradmin_site_content')
    
    context = {
        'content': content,
    }
    
    return render(request, 'majoradmin/delete_content.html', context)


# ========== County Management ==========

@major_admin_required
def county_management(request):
    """Manage counties"""
    counties = County.objects.all()
    
    search = request.GET.get('search')
    if search:
        counties = counties.filter(
            Q(name__icontains=search) | Q(code__icontains=search)
        )
    
    context = {
        'counties': counties,
    }
    
    return render(request, 'majoradmin/counties.html', context)


@major_admin_required
def create_county(request):
    """Create a new county"""
    if request.method == 'POST':
        county = County(
            name=request.POST.get('name'),
            code=request.POST.get('code'),
            is_active=request.POST.get('is_active') == 'on',
        )
        county.save()
        
        # Log the action
        AdminLog.objects.create(
            action='CREATE',
            user=request.user,
            description=f'Created county "{county.name}"',
            ip_address=get_client_ip(request)
        )
        
        messages.success(request, 'County created successfully.')
        return redirect('majoradmin_counties')
    
    return render(request, 'majoradmin/create_county.html')


@major_admin_required
def edit_county(request, county_id):
    """Edit a county"""
    county = get_object_or_404(County, id=county_id)
    
    if request.method == 'POST':
        county.name = request.POST.get('name')
        county.code = request.POST.get('code')
        county.is_active = request.POST.get('is_active') == 'on'
        county.save()
        
        messages.success(request, 'County updated successfully.')
        return redirect('majoradmin_counties')
    
    context = {
        'county': county,
    }
    
    return render(request, 'majoradmin/edit_county.html', context)


@major_admin_required
def delete_county(request, county_id):
    """Delete a county"""
    county = get_object_or_404(County, id=county_id)
    
    if request.method == 'POST':
        county.delete()
        messages.success(request, 'County deleted successfully.')
        return redirect('majoradmin_counties')
    
    context = {
        'county': county,
    }
    
    return render(request, 'majoradmin/delete_county.html', context)


# ========== User Sessions ==========

@major_admin_required
def user_sessions(request):
    """View all user sessions"""
    sessions = UserSession.objects.select_related('user').order_by('-login_time')
    
    user_filter = request.GET.get('user')
    if user_filter:
        sessions = sessions.filter(user__id=user_filter)
    
    active_filter = request.GET.get('active')
    if active_filter == 'true':
        sessions = sessions.filter(is_active=True)
    elif active_filter == 'false':
        sessions = sessions.filter(is_active=False)
    
    context = {
        'sessions': sessions,
        'users': User.objects.all(),
    }
    
    return render(request, 'majoradmin/sessions.html', context)


# ========== Database Management ==========

@major_admin_required
def database_management(request):
    """Database management - view stats and clear options"""
    from django.apps import apps
    
    # Get record counts for each model
    model_counts = {}
    for model in [User, Task, SiteContent, County, AdminLog, UserSession]:
        model_counts[model._meta.verbose_name_plural] = model.objects.count()
    
    # Get database clear logs
    clear_logs = DatabaseClearLog.objects.all()[:10]
    
    context = {
        'model_counts': model_counts,
        'clear_logs': clear_logs,
    }
    
    return render(request, 'majoradmin/database.html', context)


@major_admin_required
def clear_database(request):
    """Clear database while preserving history"""
    if request.method == 'POST':
        tables_to_clear = request.POST.getlist('tables')
        reason = request.POST.get('reason', '')
        
        records_preserved = {}
        
        # We don't actually delete records, we just log the action
        # This is a simulation for safety
        for table in tables_to_clear:
            model_name = table
            try:
                # Get the count before any hypothetical deletion
                if table == 'users':
                    count = User.objects.count()
                elif table == 'tasks':
                    count = Task.objects.count()
                elif table == 'site_content':
                    count = SiteContent.objects.count()
                elif table == 'counties':
                    count = County.objects.count()
                elif table == 'admin_logs':
                    count = AdminLog.objects.count()
                elif table == 'user_sessions':
                    count = UserSession.objects.count()
                else:
                    count = 0
                records_preserved[table] = count
            except:
                records_preserved[table] = 'Error'
        
        # Log the clear action
        DatabaseClearLog.objects.create(
            cleared_by=request.user,
            tables_cleared=tables_to_clear,
            records_preserved=records_preserved,
            reason=reason
        )
        
        # Log in admin logs
        AdminLog.objects.create(
            action='DATABASE_CLEARED',
            user=request.user,
            description=f'Database clear requested for tables: {", ".join(tables_to_clear)}',
            details={'tables': tables_to_clear, 'reason': reason},
            ip_address=get_client_ip(request)
        )
        
        messages.success(request, 'Database clear operation logged. Records preserved for history.')
        return redirect('majoradmin_database')
    
    return redirect('majoradmin_database')


# ========== Utility Functions ==========

def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
