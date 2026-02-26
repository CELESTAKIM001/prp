"""
Views for Apartment Management System
Property Manager - KIMATHI JORAM
"""

from django.shortcuts import render, redirect, get_object_or_404, Http404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.db import models
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from datetime import timedelta
from .models import (
    Property, Apartment, Tenant, Lease, 
    Payment, MaintenanceRequest, Expense, Report, UserProfile, Notification
)


def welcome(request):
    """Welcome/Landing page for non-logged in users"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'registration/welcome.html')


def super_admin_dashboard(request):
    """Super Admin Dashboard - Only accessible to superusers"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    # Get system-wide statistics
    total_users = User.objects.count()
    total_properties = Property.objects.count()
    total_apartments = Apartment.objects.count()
    total_tenants = Tenant.objects.count()
    total_payments = Payment.objects.count()
    total_expenses = Expense.objects.count()
    total_maintenance = MaintenanceRequest.objects.count()
    
    # Recent activities
    recent_payments = Payment.objects.order_by('-payment_date')[:10]
    recent_maintenance = MaintenanceRequest.objects.order_by('-created_at')[:10]
    recent_tenants = Tenant.objects.order_by('-created_at')[:10]
    
    # Revenue this month
    this_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_revenue = Payment.objects.filter(payment_date__gte=this_month).aggregate(Sum('amount'))['amount__sum'] or 0
    monthly_expenses = Expense.objects.filter(date__gte=this_month).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # All users with their roles
    all_users = User.objects.select_related('profile').order_by('-date_joined')[:50]
    
    context = {
        'total_users': total_users,
        'total_properties': total_properties,
        'total_apartments': total_apartments,
        'total_tenants': total_tenants,
        'total_payments': total_payments,
        'total_expenses': total_expenses,
        'total_maintenance': total_maintenance,
        'recent_payments': recent_payments,
        'recent_maintenance': recent_maintenance,
        'recent_tenants': recent_tenants,
        'monthly_revenue': monthly_revenue,
        'monthly_expenses': monthly_expenses,
        'net_income': monthly_revenue - monthly_expenses,
        'all_users': all_users,
    }
    return render(request, 'apartments/super_admin.html', context)


def register(request):
    """User registration view with role selection"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        role = request.POST.get('role', 'tenant')
        phone = request.POST.get('phone', '')
        national_id = request.POST.get('national_id', '')
        
        # Validate passwords
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'registration/register.html')
        
        # Check if username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'registration/register.html')
        
        # Check if email exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'registration/register.html')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name
        )
        
        # Update user profile with role (profile already created by signal)
        try:
            profile = user.profile
            profile.role = role
            profile.phone = phone
            profile.national_id = national_id
            profile.save()
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(
                user=user,
                role=role,
                phone=phone,
                national_id=national_id
            )
        
        messages.success(request, 'Account created successfully! Please login.')
        return redirect('login')
    
    return render(request, 'registration/register.html')


def dashboard(request):
    """Dashboard view showing overview based on user role"""
    
    # Require login for dashboard
    if not request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect('login')
    
    context = {}
    
    # Get counts
    context['total_properties'] = Property.objects.count()
    context['total_apartments'] = Apartment.objects.count()
    context['occupied_apartments'] = Apartment.objects.filter(status='occupied').count()
    context['available_apartments'] = Apartment.objects.filter(status='available').count()
    context['total_tenants'] = Tenant.objects.count()
    
    # Get recent payments
    context['recent_payments'] = Payment.objects.filter(status='completed').order_by('-payment_date')[:5]
    
    # Get pending maintenance requests
    context['pending_maintenance'] = MaintenanceRequest.objects.filter(
        status__in=['pending', 'in_progress']
    ).order_by('-created_at')[:5]
    
    # Calculate monthly income
    today = timezone.now()
    start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_payments = Payment.objects.filter(
        status='completed',
        payment_date__gte=start_of_month
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    monthly_expenses = Expense.objects.filter(
        expense_date__gte=start_of_month
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    context['monthly_income'] = monthly_payments
    context['monthly_expenses'] = monthly_expenses
    context['net_income'] = monthly_payments - monthly_expenses
    
    # Role-based dashboard redirect
    if request.user.is_authenticated:
        try:
            role = request.user.profile.role
            
            if role == 'owner':
                return render(request, 'apartments/dashboard_owner.html', context)
            elif role == 'tenant':
                return render(request, 'apartments/dashboard_tenant.html', context)
            elif role == 'accountant':
                return render(request, 'apartments/dashboard_accountant.html', context)
            elif role == 'maintenance':
                return render(request, 'apartments/dashboard_maintenance.html', context)
            elif role == 'security':
                return render(request, 'apartments/dashboard_security.html', context)
            elif role == 'manager':
                return render(request, 'apartments/dashboard.html', context)
            else:
                return render(request, 'apartments/dashboard.html', context)
        except:
            pass
    
    return render(request, 'apartments/dashboard.html', context)


def user_login(request):
    """User login view with role-based redirect"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Role-based redirect to specific dashboard
            try:
                profile = user.profile
                if profile.role == 'owner':
                    return redirect('dashboard')
                elif profile.role == 'tenant':
                    return redirect('dashboard')
                elif profile.role == 'manager':
                    return redirect('dashboard')
                elif profile.role == 'accountant':
                    return redirect('dashboard')
                elif profile.role == 'maintenance':
                    return redirect('dashboard')
                elif profile.role == 'security':
                    return redirect('dashboard')
                elif profile.role == 'admin':
                    return redirect('dashboard')
                else:
                    return redirect('dashboard')
            except:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'registration/login.html')


def user_logout(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('welcome')


# Terms and Conditions View (Public)
def terms(request):
    """Terms and Conditions view - public page"""
    return render(request, 'registration/terms.html')


@login_required
def notifications_list(request):
    """View user's notifications"""
    # Get notifications for this user or broadcast (recipient is null)
    notifications = Notification.objects.filter(
        models.Q(recipient=request.user) | models.Q(recipient=None, target_audience='all') | models.Q(recipient=None, target_audience='tenants') | models.Q(recipient=None, target_audience='owners') | models.Q(recipient=None, target_audience='staff')
    )
    
    # For specific audience types, filter based on user profile
    user_notifications = []
    try:
        profile = request.user.profile
        user_role = profile.role if profile else None
        
        for notif in notifications:
            if notif.recipient is not None and notif.recipient == request.user:
                user_notifications.append(notif)
            elif notif.recipient is None:  # Broadcast
                if notif.target_audience == 'all':
                    user_notifications.append(notif)
                elif notif.target_audience == 'tenants' and user_role == 'tenant':
                    user_notifications.append(notif)
                elif notif.target_audience == 'owners' and user_role == 'owner':
                    user_notifications.append(notif)
                elif notif.target_audience == 'staff' and (request.user.is_staff or request.user.is_superuser):
                    user_notifications.append(notif)
    except:
        # If no profile, just show broadcast notifications
        user_notifications = Notification.objects.filter(recipient=None)
    
    # Get unique notifications
    notifications = list(set(user_notifications))
    notifications.sort(key=lambda x: x.created_at, reverse=True)
    
    unread_count = sum(1 for n in notifications if not n.is_read)
    
    # Mark all as read
    if request.method == 'POST' and 'mark_all_read' in request.POST:
        for notif in notifications:
            if not notif.is_read:
                notif.is_read = True
                notif.save()
        messages.success(request, 'All notifications marked as read')
    
    context = {
        'notifications': notifications[:50],
        'unread_count': unread_count,
    }
    return render(request, 'apartments/notifications.html', context)


@login_required
def notification_mark_read(request, pk):
    """Mark a notification as read"""
    # Get notification for this user or broadcast
    notification = Notification.objects.filter(
        models.Q(pk=pk) & (models.Q(recipient=request.user) | models.Q(recipient=None))
    ).first()
    
    if not notification:
        raise Http404("Notification not found")
    
    notification.is_read = True
    notification.save()
    
    if notification.link:
        return redirect(notification.link)
    return redirect('notifications_list')


@login_required
def create_notification(request):
    """Create and broadcast notifications to users"""
    # Check if user has permission (admin, owner, or staff)
    if not request.user.is_staff and not request.user.is_superuser:
        # Check if user is an owner
        try:
            profile = request.user.profile
            if profile.role != 'owner':
                messages.error(request, 'You do not have permission to create notifications.')
                return redirect('dashboard')
        except:
            messages.error(request, 'You do not have permission to create notifications.')
            return redirect('dashboard')
    
    if request.method == 'POST':
        form_data = request.POST
        
        notification_type = form_data.get('notification_type')
        target_audience = form_data.get('target_audience')
        title = form_data.get('title')
        message = form_data.get('message')
        description = form_data.get('description', '')
        link = form_data.get('link', '')
        image_url = form_data.get('image_url', '')
        
        # Get social links
        social_links = {}
        social_fields = ['facebook', 'twitter', 'instagram', 'linkedin', 'youtube', 'tiktok', 'whatsapp', 'telegram']
        for field in social_fields:
            value = form_data.get(f'social_{field}', '').strip()
            if value:
                social_links[field] = value
        
        # Get specific user if targeted
        recipient_username = form_data.get('recipient_username', '')
        
        # Create notifications based on target audience
        created_count = 0
        
        if target_audience == 'specific' and recipient_username:
            # Send to specific user
            try:
                recipient = User.objects.get(username=recipient_username)
                Notification.objects.create(
                    recipient=recipient,
                    recipient_username=recipient_username,
                    notification_type=notification_type,
                    target_audience=target_audience,
                    title=title,
                    message=message,
                    description=description,
                    link=link,
                    image_url=image_url,
                    social_links=social_links if social_links else {}
                )
                created_count = 1
                messages.success(request, f'Notification sent to {recipient_username}')
            except User.DoesNotExist:
                messages.error(request, f'User {recipient_username} not found')
        else:
            # Get users based on target audience
            if target_audience == 'all':
                users = User.objects.all()
            elif target_audience == 'tenants':
                # Get tenants from profiles
                tenant_profiles = UserProfile.objects.filter(role='tenant')
                users = User.objects.filter(profile__in=tenant_profiles)
            elif target_audience == 'owners':
                owner_profiles = UserProfile.objects.filter(role='owner')
                users = User.objects.filter(profile__in=owner_profiles)
            elif target_audience == 'staff':
                users = User.objects.filter(is_staff=True)
            else:
                users = User.objects.all()
            
            # Create notification for each user
            for user in users:
                Notification.objects.create(
                    recipient=user,
                    notification_type=notification_type,
                    target_audience=target_audience,
                    title=title,
                    message=message,
                    description=description,
                    link=link,
                    image_url=image_url,
                    social_links=social_links if social_links else {}
                )
                created_count += 1
            
            messages.success(request, f'Notification broadcast to {created_count} users')
        
        return redirect('dashboard')
    
    context = {
        'notification_types': Notification.NOTIFICATION_TYPES,
        'target_audiences': Notification.TARGET_AUDIENCE,
    }
    return render(request, 'apartments/create_notification.html', context)


@login_required
def profile_view(request):
    """View user profile"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    context = {
        'profile': profile,
    }
    return render(request, 'apartments/profile.html', context)


@login_required
def profile_edit(request):
    """Edit user profile"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        # Update user fields
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        
        # Update profile fields
        profile.phone = request.POST.get('phone', '')
        profile.national_id = request.POST.get('national_id', '')
        profile.address = request.POST.get('address', '')
        profile.city = request.POST.get('city', '')
        profile.county = request.POST.get('county', '')
        profile.postal_code = request.POST.get('postal_code', '')
        profile.emergency_contact_name = request.POST.get('emergency_contact_name', '')
        profile.emergency_contact_phone = request.POST.get('emergency_contact_phone', '')
        profile.emergency_contact_relation = request.POST.get('emergency_contact_relation', '')
        
        # Banking info
        profile.bank_name = request.POST.get('bank_name', '')
        profile.account_number = request.POST.get('account_number', '')
        profile.bank_branch = request.POST.get('bank_branch', '')
        profile.mpesa_paybill = request.POST.get('mpesa_paybill', '')
        profile.mpesa_till = request.POST.get('mpesa_till', '')
        
        profile.save()
        
        messages.success(request, 'Profile updated successfully')
        return redirect('profile')
    
    context = {
        'profile': profile,
    }
    return render(request, 'apartments/profile_form.html', context)


# Property Views
class PropertyListView(ListView):
    model = Property
    template_name = 'apartments/property_list.html'
    context_object_name = 'properties'
    paginate_by = 10


class PropertyDetailView(DetailView):
    model = Property
    template_name = 'apartments/property_detail.html'
    context_object_name = 'property'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['apartments'] = self.object.apartments.all()
        return context


class PropertyCreateView(CreateView):
    model = Property
    fields = ['name', 'property_type', 'address', 'latitude', 'longitude', 'total_units', 
              'description', 'title_deed_number', 'water_account', 'electricity_account', 'owner']
    template_name = 'apartments/property_form.html'
    success_url = '/properties/'
    
    def form_valid(self, form):
        messages.success(self.request, 'Property created successfully!')
        return super().form_valid(form)


class PropertyUpdateView(UpdateView):
    model = Property
    fields = ['name', 'property_type', 'address', 'latitude', 'longitude', 'total_units', 
              'description', 'title_deed_number', 'water_account', 'electricity_account', 'owner']
    template_name = 'apartments/property_form.html'
    success_url = '/properties/'
    
    def form_valid(self, form):
        messages.success(self.request, 'Property updated successfully!')
        return super().form_valid(form)


# GIS Dashboard View
def gis_dashboard(request):
    """GIS Dashboard view showing property locations on a map"""
    
    # Require login for GIS dashboard
    if not request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect('login')
    
    properties = Property.objects.exclude(latitude__isnull=True, longitude__isnull=True)
    all_properties = Property.objects.all()
    
    # Convert to GeoJSON-like format for map display
    property_locations = []
    for prop in properties:
        property_locations.append({
            'id': prop.id,
            'name': prop.name,
            'address': prop.address,
            'lat': float(prop.latitude) if prop.latitude else None,
            'lng': float(prop.longitude) if prop.longitude else None,
            'total_units': prop.total_units,
            'apartments': prop.apartments.count(),
        })
    
    context = {
        'properties': all_properties,
        'property_locations': property_locations,
        'has_locations': len(property_locations) > 0,
    }
    
    return render(request, 'apartments/gis_dashboard.html', context)


def update_property_location(request, pk):
    """Update property location coordinates via AJAX"""
    if request.method == 'POST':
        property_obj = get_object_or_404(Property, pk=pk)
        lat = request.POST.get('latitude')
        lng = request.POST.get('longitude')
        
        if lat and lng:
            try:
                property_obj.latitude = float(lat)
                property_obj.longitude = float(lng)
                property_obj.save()
                messages.success(request, f'Location updated for {property_obj.name}')
            except ValueError:
                messages.error(request, 'Invalid coordinates')
        else:
            messages.error(request, 'Please provide valid coordinates')
    
    return redirect('gis_dashboard')


# Apartment Views
class ApartmentListView(ListView):
    model = Apartment
    template_name = 'apartments/apartment_list.html'
    context_object_name = 'apartments'
    paginate_by = 10
    
    def get_queryset(self):
        user = self.request.user
        
        # Staff, superusers can see all apartments
        if user.is_superuser or user.is_staff:
            queryset = Apartment.objects.select_related('property').all()
        else:
            try:
                profile = user.profile
                if profile.role == 'owner':
                    # Owners can see their own apartments
                    queryset = Apartment.objects.select_related('property').filter(property__owner=user)
                elif profile.role == 'tenant':
                    # Tenants can only see their own apartment
                    from django.utils import timezone
                    today = timezone.now().date()
                    tenant_lease = Lease.objects.filter(
                        tenant__user=user,
                        status='active',
                        start_date__lte=today,
                        end_date__gte=today
                    ).first()
                    
                    if tenant_lease:
                        queryset = Apartment.objects.filter(id=tenant_lease.apartment.id)
                    else:
                        queryset = Apartment.objects.none()
                elif profile.role in ['manager', 'accountant', 'maintenance', 'security']:
                    # These roles can see all apartments
                    queryset = Apartment.objects.select_related('property').all()
                else:
                    queryset = Apartment.objects.none()
            except UserProfile.DoesNotExist:
                queryset = Apartment.objects.none()
        
        # Apply filters
        status = self.request.GET.get('status')
        property_id = self.request.GET.get('property')
        if status:
            queryset = queryset.filter(status=status)
        if property_id:
            queryset = queryset.filter(property_id=property_id)
        return queryset


class ApartmentDetailView(DetailView):
    model = Apartment
    template_name = 'apartments/apartment_detail.html'
    context_object_name = 'apartment'
    
    def get_object(self, queryset=None):
        user = self.request.user
        obj = super().get_object(queryset)
        
        # Check access permissions
        if user.is_superuser or user.is_staff:
            return obj
        
        try:
            profile = user.profile
            if profile.role == 'owner':
                # Owner can only view their own apartments
                if obj.property.owner != user:
                    from django.shortcuts import Http404
                    raise Http404("You don't have permission to view this apartment.")
            elif profile.role == 'tenant':
                # Tenant can only view their own apartment
                from django.utils import timezone
                today = timezone.now().date()
                tenant_lease = Lease.objects.filter(
                    tenant__user=user,
                    status='active',
                    start_date__lte=today,
                    end_date__gte=today
                ).first()
                
                if not tenant_lease or obj.id != tenant_lease.apartment.id:
                    from django.shortcuts import Http404
                    raise Http404("You don't have permission to view this apartment.")
            elif profile.role in ['manager', 'accountant', 'maintenance', 'security']:
                # These roles can view all
                return obj
            else:
                from django.shortcuts import Http404
                raise Http404("You don't have permission to view this apartment.")
        except UserProfile.DoesNotExist:
            from django.shortcuts import Http404
            raise Http404("You don't have permission to view this apartment.")
        
        return obj


class ApartmentCreateView(CreateView):
    model = Apartment
    fields = ['property', 'unit_number', 'floor', 'apartment_type', 'bedrooms', 
              'bathrooms', 'area_sqft', 'rent_amount', 'deposit_amount', 'status', 
              'description', 'has_water', 'has_electricity', 'has_wifi', 'has_parking']
    template_name = 'apartments/apartment_form.html'
    success_url = '/apartments/'
    
    def dispatch(self, request, *args, **kwargs):
        # Only admin/staff/owner/manager can create apartments
        if not request.user.is_superuser and not request.user.is_staff:
            try:
                profile = request.user.profile
                if profile.role not in ['owner', 'manager']:
                    messages.error(request, 'Only administrators and property owners can create apartments.')
                    from django.shortcuts import redirect
                    return redirect('apartment_list')
            except UserProfile.DoesNotExist:
                messages.error(request, 'You do not have permission to create apartments.')
                from django.shortcuts import redirect
                return redirect('apartment_list')
        return super().dispatch(request, *args, **kwargs)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        
        # Restrict property choices for owners
        if user.is_superuser or user.is_staff:
            pass
        else:
            try:
                profile = user.profile
                if profile.role == 'owner':
                    form.fields['property'].queryset = Property.objects.filter(owner=user)
            except UserProfile.DoesNotExist:
                form.fields['property'].queryset = Property.objects.none()
        
        return form
    
    def form_valid(self, form):
        messages.success(self.request, 'Apartment created successfully!')
        return super().form_valid(form)


# Tenant Views
class TenantListView(ListView):
    model = Tenant
    template_name = 'apartments/tenant_list.html'
    context_object_name = 'tenants'
    paginate_by = 10
    
    def get_queryset(self):
        user = self.request.user
        
        # Staff, superusers, owners can see tenants
        if user.is_superuser or user.is_staff:
            queryset = Tenant.objects.all()
        else:
            try:
                profile = user.profile
                if profile.role == 'owner':
                    # Owners can see tenants in their properties
                    queryset = Tenant.objects.filter(
                        leases__apartment__property__owner=user
                    ).distinct()
                elif profile.role == 'manager':
                    # Managers can see all tenants
                    queryset = Tenant.objects.all()
                else:
                    # Tenants and other roles cannot see tenant list
                    queryset = Tenant.objects.none()
            except UserProfile.DoesNotExist:
                queryset = Tenant.objects.none()
        
        return queryset


class TenantDetailView(DetailView):
    model = Tenant
    template_name = 'apartments/tenant_detail.html'
    context_object_name = 'tenant'
    
    def get_object(self, queryset=None):
        user = self.request.user
        obj = super().get_object(queryset)
        
        # Check access permissions
        if user.is_superuser or user.is_staff:
            return obj
        
        try:
            profile = user.profile
            if profile.role == 'owner':
                # Owner can only view tenants in their properties
                if not obj.leases.filter(apartment__property__owner=user).exists():
                    from django.shortcuts import Http404
                    raise Http404("You don't have permission to view this tenant.")
            elif profile.role == 'tenant':
                # Tenant can only view their own profile
                if obj.user != user:
                    from django.shortcuts import Http404
                    raise Http404("You don't have permission to view this tenant.")
            else:
                # Other roles without permission
                from django.shortcuts import Http404
                raise Http404("You don't have permission to view this tenant.")
        except UserProfile.DoesNotExist:
            from django.shortcuts import Http404
            raise Http404("You don't have permission to view this tenant.")
        
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['leases'] = self.object.leases.all()[:5]
        return context


class TenantCreateView(CreateView):
    model = Tenant
    fields = ['first_name', 'last_name', 'email', 'phone', 'alternative_phone',
              'gender', 'id_number', 'date_of_birth', 'occupation', 'employer',
              'monthly_income', 'employer_contact', 'next_of_kin_name', 'next_of_kin_contact',
              'emergency_contact_name', 'emergency_contact_phone', 'id_copy', 'lease_agreement', 'photo']
    template_name = 'apartments/tenant_form.html'
    success_url = '/tenants/'
    
    def dispatch(self, request, *args, **kwargs):
        # Only admin/staff can create tenants
        if not request.user.is_superuser and not request.user.is_staff:
            messages.error(request, 'Only administrators can create tenant records.')
            from django.shortcuts import redirect
            return redirect('tenant_list')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, 'Tenant created successfully!')
        return super().form_valid(form)


# Lease Views
class LeaseListView(ListView):
    model = Lease
    template_name = 'apartments/lease_list.html'
    context_object_name = 'leases'
    paginate_by = 10
    
    def get_queryset(self):
        user = self.request.user
        
        # Staff, superusers can see all leases
        if user.is_superuser or user.is_staff:
            queryset = Lease.objects.select_related('apartment', 'tenant').all()
        else:
            try:
                profile = user.profile
                if profile.role == 'owner':
                    # Owners can see leases for their properties
                    queryset = Lease.objects.select_related(
                        'apartment', 'tenant'
                    ).filter(apartment__property__owner=user)
                elif profile.role == 'manager':
                    # Managers can see all leases
                    queryset = Lease.objects.select_related('apartment', 'tenant').all()
                elif profile.role == 'tenant':
                    # Tenants can only see their own lease
                    from django.utils import timezone
                    today = timezone.now().date()
                    queryset = Lease.objects.select_related(
                        'apartment', 'tenant'
                    ).filter(tenant__user=user)
                else:
                    queryset = Lease.objects.none()
            except UserProfile.DoesNotExist:
                queryset = Lease.objects.none()
        
        return queryset


class LeaseCreateView(CreateView):
    model = Lease
    fields = ['apartment', 'tenant', 'start_date', 'end_date', 'rent_amount', 
              'deposit_amount', 'status', 'auto_renew', 'notice_period_days', 'terms']
    template_name = 'apartments/lease_form.html'
    success_url = '/leases/'
    
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        
        # Check if user has permission to create leases
        if user.is_superuser or user.is_staff:
            return super().dispatch(request, *args, **kwargs)
        
        try:
            profile = user.profile
            # Check explicit permission or role-based access
            if profile.can_create_lease:
                return super().dispatch(request, *args, **kwargs)
            elif profile.role == 'owner':
                return super().dispatch(request, *args, **kwargs)
            elif profile.role == 'manager':
                if profile.assigned_property:
                    return super().dispatch(request, *args, **kwargs)
                else:
                    messages.error(request, 'You must be assigned a property to create leases.')
                    from django.shortcuts import redirect
                    return redirect('lease_list')
            else:
                messages.error(request, 'You do not have permission to create lease agreements.')
                from django.shortcuts import redirect
                return redirect('lease_list')
        except UserProfile.DoesNotExist:
            messages.error(request, 'You do not have permission to create leases.')
            from django.shortcuts import redirect
            return redirect('lease_list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        
        # Restrict choices based on user role
        if user.is_superuser or user.is_staff:
            pass
        else:
            try:
                profile = user.profile
                if profile.role == 'owner':
                    form.fields['apartment'].queryset = Apartment.objects.filter(property__owner=user)
                elif profile.role == 'manager' and profile.assigned_property:
                    # Managers can only select apartments in their assigned property
                    form.fields['apartment'].queryset = Apartment.objects.filter(
                        property=profile.assigned_property
                    )
            except UserProfile.DoesNotExist:
                form.fields['apartment'].queryset = Apartment.objects.none()
        
        return form
    
    def form_valid(self, form):
        lease = form.save(commit=False)
        messages.success(self.request, 'Lease created successfully!')
        
        # Update apartment status to occupied if lease is active
        if lease.status == 'active':
            Apartment.objects.filter(pk=lease.apartment.pk).update(status='occupied')
        
        # Create notification
        Notification.objects.create(
            recipient=lease.tenant.user if lease.tenant.user else None,
            notification_type='lease',
            title='New Lease Created',
            message=f'A new lease has been created for {lease.apartment}',
            link=f'/leases/{lease.pk}/'
        )
        
        lease.save()
        return redirect(self.success_url)


# Payment Views
class PaymentListView(ListView):
    model = Payment
    template_name = 'apartments/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 10
    
    def get_queryset(self):
        user = self.request.user
        
        # Staff and superusers can see all payments
        if user.is_superuser or user.is_staff:
            queryset = Payment.objects.select_related('lease__apartment', 'lease__tenant').all()
        else:
            try:
                profile = user.profile
                
                # Managers with assigned property can see payments for their property
                if profile.role == 'manager' and profile.assigned_property:
                    queryset = Payment.objects.select_related(
                        'lease__apartment', 'lease__tenant'
                    ).filter(lease__apartment__property=profile.assigned_property)
                # Owners can see payments for their properties
                elif profile.role == 'owner':
                    queryset = Payment.objects.select_related(
                        'lease__apartment', 'lease__tenant'
                    ).filter(lease__apartment__property__owner=user)
                # Accountants see all payments
                elif profile.role == 'accountant':
                    queryset = Payment.objects.select_related('lease__apartment', 'lease__tenant').all()
                # Tenants can ONLY see their own payments
                elif profile.role == 'tenant':
                    from django.utils import timezone
                    today = timezone.now().date()
                    tenant_lease = Lease.objects.filter(
                        tenant__user=user,
                        status='active',
                        start_date__lte=today,
                        end_date__gte=today
                    ).first()
                    
                    if tenant_lease:
                        queryset = Payment.objects.select_related(
                            'lease__apartment', 'lease__tenant'
                        ).filter(lease=tenant_lease)
                    else:
                        queryset = Payment.objects.none()
                else:
                    queryset = Payment.objects.select_related('lease__apartment', 'lease__tenant').all()
            except UserProfile.DoesNotExist:
                queryset = Payment.objects.none()
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset


class PaymentCreateView(CreateView):
    model = Payment
    fields = ['lease', 'amount', 'payment_date', 'payment_method', 
              'reference_number', 'status', 'receipt_number', 'notes']
    template_name = 'apartments/payment_form.html'
    success_url = '/payments/'
    
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        
        # Check if user has permission to create payments
        if not user.is_superuser and not user.is_staff:
            try:
                profile = user.profile
                # Admin/manager with permission OR owner can create payments
                if profile.role == 'manager' and profile.assigned_property:
                    # Manager with assigned property can create
                    return super().dispatch(request, *args, **kwargs)
                elif profile.can_create_payment:
                    # Has explicit permission
                    return super().dispatch(request, *args, **kwargs)
                else:
                    messages.error(request, 'You do not have permission to create payment records.')
                    from django.shortcuts import redirect
                    return redirect('payment_list')
            except UserProfile.DoesNotExist:
                messages.error(request, 'You do not have permission to create payment records.')
                from django.shortcuts import redirect
                return redirect('payment_list')
        return super().dispatch(request, *args, **kwargs)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        
        # Restrict lease choices based on user role
        if user.is_superuser or user.is_staff:
            pass
        else:
            try:
                profile = user.profile
                
                if profile.role == 'manager' and profile.assigned_property:
                    # Managers can only select leases for their assigned property
                    form.fields['lease'].queryset = Lease.objects.filter(
                        apartment__property=profile.assigned_property, status='active'
                    ).select_related('apartment', 'tenant')
                elif profile.role == 'owner':
                    # Owners can select leases for their properties
                    form.fields['lease'].queryset = Lease.objects.filter(
                        apartment__property__owner=user, status='active'
                    ).select_related('apartment', 'tenant')
            except UserProfile.DoesNotExist:
                form.fields['lease'].queryset = Lease.objects.none()
        
        return form
    
    def form_valid(self, form):
        payment = form.save(commit=False)
        
        # Create notification on payment completion
        if payment.status == 'completed':
            Notification.objects.create(
                recipient=payment.lease.tenant.user if payment.lease.tenant.user else None,
                notification_type='payment',
                title='Payment Received',
                message=f'Payment of {payment.amount} has been received',
                link=f'/payments/{payment.pk}/'
            )
        
        messages.success(self.request, 'Payment recorded successfully!')
        return super().form_valid(form)


# Maintenance Views
class MaintenanceListView(ListView):
    model = MaintenanceRequest
    template_name = 'apartments/maintenance_list.html'
    context_object_name = 'maintenance_requests'
    paginate_by = 10
    
    def get_queryset(self):
        user = self.request.user
        
        # Staff and superusers can see all maintenance requests
        if user.is_superuser or user.is_staff:
            queryset = MaintenanceRequest.objects.select_related('apartment__property', 'tenant').all()
        else:
            try:
                profile = user.profile
                
                # Owners can see maintenance for their properties
                if profile.role == 'owner':
                    queryset = MaintenanceRequest.objects.select_related(
                        'apartment__property', 'tenant'
                    ).filter(apartment__property__owner=user)
                # Maintenance staff can see assigned requests
                elif profile.role == 'maintenance':
                    queryset = MaintenanceRequest.objects.select_related(
                        'apartment__property', 'tenant'
                    ).filter(assigned_to=user)
                # Tenants can ONLY see their own apartment's maintenance requests
                elif profile.role == 'tenant':
                    # Get tenant's apartment via active lease
                    from django.utils import timezone
                    today = timezone.now().date()
                    tenant_lease = Lease.objects.filter(
                        tenant__user=user,
                        status='active',
                        start_date__lte=today,
                        end_date__gte=today
                    ).first()
                    
                    if tenant_lease:
                        # Tenant can only see maintenance for their own apartment
                        queryset = MaintenanceRequest.objects.select_related(
                            'apartment__property', 'tenant'
                        ).filter(apartment=tenant_lease.apartment)
                    else:
                        # No active lease - return empty queryset
                        queryset = MaintenanceRequest.objects.none()
                else:
                    # Other roles (security, accountant, manager) see all
                    queryset = MaintenanceRequest.objects.select_related('apartment__property', 'tenant').all()
            except UserProfile.DoesNotExist:
                queryset = MaintenanceRequest.objects.none()
        
        # Apply filters
        status = self.request.GET.get('status')
        priority = self.request.GET.get('priority')
        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        
        return queryset


class MaintenanceCreateView(CreateView):
    model = MaintenanceRequest
    fields = ['apartment', 'tenant', 'title', 'description', 'category', 'priority', 'status',
              'assigned_to', 'assigned_to_name', 'estimated_cost', 'scheduled_date', 
              'before_image', 'notes']
    template_name = 'apartments/maintenance_form.html'
    success_url = '/maintenance/'
    
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        
        # Check if user has permission to create maintenance
        if not user.is_superuser and not user.is_staff:
            try:
                profile = user.profile
                # Check explicit permission
                if profile.can_create_maintenance:
                    return super().dispatch(request, *args, **kwargs)
                # Role-based access for tenant (can always create for own apartment)
                elif profile.role == 'tenant':
                    return super().dispatch(request, *args, **kwargs)
                # Owner/manager with assigned property
                elif profile.role in ['owner', 'manager']:
                    if profile.role == 'manager' and not profile.assigned_property:
                        messages.error(request, 'You must be assigned a property to create maintenance requests.')
                        from django.shortcuts import redirect
                        return redirect('maintenance_list')
                    return super().dispatch(request, *args, **kwargs)
                # Maintenance staff
                elif profile.role == 'maintenance':
                    return super().dispatch(request, *args, **kwargs)
                else:
                    messages.error(request, 'You do not have permission to create maintenance requests.')
                    from django.shortcuts import redirect
                    return redirect('maintenance_list')
            except UserProfile.DoesNotExist:
                messages.error(request, 'You do not have permission to create maintenance requests.')
                from django.shortcuts import redirect
                return redirect('maintenance_list')
        return super().dispatch(request, *args, **kwargs)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        
        # Restrict apartment choices based on user role
        if user.is_superuser or user.is_staff:
            # Admin/Staff can select any apartment
            pass
        else:
            try:
                profile = user.profile
                
                if profile.role == 'tenant':
                    # Tenants can ONLY create maintenance for their own apartment
                    from django.utils import timezone
                    today = timezone.now().date()
                    tenant_lease = Lease.objects.filter(
                        tenant__user=user,
                        status='active',
                        start_date__lte=today,
                        end_date__gte=today
                    ).first()
                    
                    if tenant_lease:
                        # Only show their apartment
                        form.fields['apartment'].queryset = Apartment.objects.filter(id=tenant_lease.apartment.id)
                        # Auto-fill tenant
                        try:
                            tenant = Tenant.objects.get(user=user)
                            form.fields['tenant'].queryset = Tenant.objects.filter(id=tenant.id)
                        except Tenant.DoesNotExist:
                            form.fields['tenant'].queryset = Tenant.objects.none()
                    else:
                        # No active lease - no apartments available
                        form.fields['apartment'].queryset = Apartment.objects.none()
                        form.fields['tenant'].queryset = Tenant.objects.none()
                        messages.error(self.request, 'You do not have an active lease. Cannot create maintenance requests.')
                elif profile.role == 'owner':
                    # Owners can only select their apartments
                    form.fields['apartment'].queryset = Apartment.objects.filter(property__owner=user)
                elif profile.role == 'manager':
                    # Managers can only select apartments in their assigned property
                    if profile.assigned_property:
                        form.fields['apartment'].queryset = Apartment.objects.filter(
                            property=profile.assigned_property
                        )
                    else:
                        form.fields['apartment'].queryset = Apartment.objects.none()
                        messages.error(self.request, 'You must be assigned a property to create maintenance requests.')
                elif profile.role == 'maintenance':
                    # Maintenance staff can see all apartments
                    pass
                else:
                    # Other roles - restrict to all apartments
                    pass
            except UserProfile.DoesNotExist:
                form.fields['apartment'].queryset = Apartment.objects.none()
                form.fields['tenant'].queryset = Tenant.objects.none()
        
        return form
    
    def form_valid(self, form):
        user = self.request.user
        
        # Additional security check: Verify tenant owns the apartment
        if not user.is_superuser and not user.is_staff:
            try:
                profile = user.profile
                if profile.role == 'tenant':
                    maintenance = form.save(commit=False)
                    from django.utils import timezone
                    today = timezone.now().date()
                    tenant_lease = Lease.objects.filter(
                        tenant__user=user,
                        status='active',
                        start_date__lte=today,
                        end_date__gte=today
                    ).first()
                    
                    if not tenant_lease or maintenance.apartment.id != tenant_lease.apartment.id:
                        messages.error(self.request, 'You can only create maintenance requests for your own apartment.')
                        return redirect('maintenance_list')
                elif profile.role == 'manager':
                    # Managers can only create for their assigned property
                    if profile.assigned_property:
                        maintenance = form.save(commit=False)
                        if maintenance.apartment.property != profile.assigned_property:
                            messages.error(self.request, 'You can only create maintenance requests for your assigned property.')
                            return redirect('maintenance_list')
                    else:
                        messages.error(self.request, 'You must be assigned a property to create maintenance requests.')
                        return redirect('maintenance_list')
            except UserProfile.DoesNotExist:
                pass
        
        maintenance = form.save(commit=False)
        
        # Create notification
        if maintenance.assigned_to:
            Notification.objects.create(
                recipient=maintenance.assigned_to,
                notification_type='maintenance',
                title='New Maintenance Assignment',
                message=f'You have been assigned to: {maintenance.title}',
                link=f'/maintenance/{maintenance.pk}/'
            )
        
        messages.success(self.request, 'Maintenance request created successfully!')
        return super().form_valid(form)


# Expense Views
class ExpenseListView(ListView):
    model = Expense
    template_name = 'apartments/expense_list.html'
    context_object_name = 'expenses'
    paginate_by = 10


class ExpenseCreateView(CreateView):
    model = Expense
    fields = ['property', 'category', 'description', 'amount', 'expense_date',
              'vendor', 'receipt_number', 'receipt_image', 'approved_by']
    template_name = 'apartments/expense_form.html'
    success_url = '/expenses/'
    
    def form_valid(self, form):
        messages.success(self.request, 'Expense recorded successfully!')
        return super().form_valid(form)


# Report Views
@login_required
def reports_view(request):
    """Generate reports view"""
    report_type = request.GET.get('type', 'income')
    property_id = request.GET.get('property')
    
    context = {'report_type': report_type}
    context['properties'] = Property.objects.all()
    
    if property_id:
        property_obj = get_object_or_404(Property, pk=property_id)
        context['selected_property'] = property_obj
    else:
        property_obj = None
    
    # Generate report data
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    end_of_month = today
    
    if report_type == 'income':
        payments = Payment.objects.filter(status='completed', payment_date__gte=start_of_month)
        if property_obj:
            payments = payments.filter(lease__apartment__property=property_obj)
        
        total_income = payments.aggregate(total=Sum('amount'))['total'] or 0
        context['total_income'] = total_income
        context['payments'] = payments[:20]
        
    elif report_type == 'occupancy':
        apartments = Apartment.objects.all()
        if property_obj:
            apartments = apartments.filter(property=property_obj)
        
        total = apartments.count()
        occupied = apartments.filter(status='occupied').count()
        context['total_apartments'] = total
        context['occupied_apartments'] = occupied
        context['available_apartments'] = total - occupied
        context['occupancy_rate'] = (occupied / total * 100) if total > 0 else 0
        
    elif report_type == 'maintenance':
        maintenance = MaintenanceRequest.objects.all()
        if property_obj:
            maintenance = maintenance.filter(apartment__property=property_obj)
        
        context['total_requests'] = maintenance.count()
        context['pending'] = maintenance.filter(status='pending').count()
        context['in_progress'] = maintenance.filter(status='in_progress').count()
        context['completed'] = maintenance.filter(status='completed').count()
        context['maintenance_requests'] = maintenance[:20]
        
    elif report_type == 'financial':
        payments = Payment.objects.filter(status='completed', payment_date__gte=start_of_month)
        expenses = Expense.objects.filter(expense_date__gte=start_of_month)
        
        if property_obj:
            payments = payments.filter(lease__apartment__property=property_obj)
            expenses = expenses.filter(property=property_obj)
        
        total_income = payments.aggregate(total=Sum('amount'))['total'] or 0
        total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
        
        context['total_income'] = total_income
        context['total_expenses'] = total_expenses
        context['net_income'] = total_income - total_expenses
        context['expenses'] = expenses[:20]
    
    return render(request, 'apartments/reports.html', context)
