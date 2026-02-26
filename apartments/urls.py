"""
URL configuration for Apartment Management System
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Welcome/Landing page (for non-logged in users)
    path('', views.welcome, name='welcome'),
    
    # Dashboard (requires login)
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Authentication
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('terms/', views.terms, name='terms'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
    
    # Profile
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    
    # Settings (redirect to profile)
    path('settings/', views.profile_edit, name='settings'),
    
    # Notifications
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/create/', views.create_notification, name='create_notification'),
    path('notifications/<int:pk>/read/', views.notification_mark_read, name='notification_mark_read'),
    
    # Properties
    path('properties/', views.PropertyListView.as_view(), name='property_list'),
    path('properties/create/', views.PropertyCreateView.as_view(), name='property_create'),
    path('properties/<int:pk>/', views.PropertyDetailView.as_view(), name='property_detail'),
    path('properties/<int:pk>/update/', views.PropertyUpdateView.as_view(), name='property_update'),
    
    # Apartments
    path('apartments/', views.ApartmentListView.as_view(), name='apartment_list'),
    path('apartments/create/', views.ApartmentCreateView.as_view(), name='apartment_create'),
    path('apartments/<int:pk>/', views.ApartmentDetailView.as_view(), name='apartment_detail'),
    
    # Tenants
    path('tenants/', views.TenantListView.as_view(), name='tenant_list'),
    path('tenants/create/', views.TenantCreateView.as_view(), name='tenant_create'),
    path('tenants/<int:pk>/', views.TenantDetailView.as_view(), name='tenant_detail'),
    
    # Leases
    path('leases/', views.LeaseListView.as_view(), name='lease_list'),
    path('leases/create/', views.LeaseCreateView.as_view(), name='lease_create'),
    
    # Payments
    path('payments/', views.PaymentListView.as_view(), name='payment_list'),
    path('payments/create/', views.PaymentCreateView.as_view(), name='payment_create'),
    
    # Maintenance
    path('maintenance/', views.MaintenanceListView.as_view(), name='maintenance_list'),
    path('maintenance/create/', views.MaintenanceCreateView.as_view(), name='maintenance_create'),
    
    # Expenses
    path('expenses/', views.ExpenseListView.as_view(), name='expense_list'),
    path('expenses/create/', views.ExpenseCreateView.as_view(), name='expense_create'),
    
    # Reports
    path('reports/', views.reports_view, name='reports'),
    
    # GIS Dashboard
    path('gis/', views.gis_dashboard, name='gis_dashboard'),
    path('gis/update-location/<int:pk>/', views.update_property_location, name='update_property_location'),
]
