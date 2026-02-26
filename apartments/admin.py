"""
Admin configuration for Apartment Management System
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    UserProfile, Notification, Property, Apartment, Tenant, 
    Lease, Payment, MaintenanceRequest, Expense, Report
)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fieldsets = (
        ('Role & Permissions', {
            'fields': ('role', 'phone', 'national_id', 'profile_photo')
        }),
        ('Personal Details', {
            'fields': ('date_of_birth', 'address', 'city', 'county', 'postal_code')
        }),
        ('Professional Details', {
            'fields': ('kra_pin', 'years_experience', 'company_name', 'license_number', 'skill_type'),
            'classes': ('collapse',)
        }),
        ('Banking Information', {
            'fields': ('bank_name', 'account_number', 'bank_branch', 'mpesa_paybill', 'mpesa_till'),
            'classes': ('collapse',)
        }),
        ('Access Permissions', {
            'fields': ('can_add_tenants', 'can_approve_payments', 'can_view_reports')
        }),
        ('Work Details', {
            'fields': ('assigned_property', 'availability_status', 'shift', 'supervisor_name', 'assigned_gate'),
            'classes': ('collapse',)
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation'),
            'classes': ('collapse',)
        }),
    )


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    
    def get_role(self, obj):
        try:
            return obj.profile.get_role_display()
        except:
            return '-'
    get_role.short_description = 'Role'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'national_id', 'assigned_property', 'availability_status')
    list_filter = ('role', 'availability_status')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone')
    raw_id_fields = ('user', 'assigned_property')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('recipient__username', 'title', 'message')
    raw_id_fields = ('recipient',)


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'property_type', 'total_units', 'owner', 'created_at')
    list_filter = ('property_type',)
    search_fields = ('name', 'address', 'title_deed_number')
    raw_id_fields = ('owner',)


@admin.register(Apartment)
class ApartmentAdmin(admin.ModelAdmin):
    list_display = ('property', 'unit_number', 'apartment_type', 'bedrooms', 'rent_amount', 'status')
    list_filter = ('status', 'apartment_type', 'property')
    search_fields = ('unit_number', 'property__name')
    raw_id_fields = ('property',)


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'id_number', 'created_at')
    list_filter = ('gender',)
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'id_number')
    raw_id_fields = ('user',)


@admin.register(Lease)
class LeaseAdmin(admin.ModelAdmin):
    list_display = ('apartment', 'tenant', 'start_date', 'end_date', 'rent_amount', 'status')
    list_filter = ('status',)
    search_fields = ('apartment__property__name', 'tenant__first_name', 'tenant__last_name')
    raw_id_fields = ('apartment', 'tenant')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('lease', 'amount', 'payment_date', 'payment_method', 'status', 'reference_number')
    list_filter = ('status', 'payment_method')
    search_fields = ('reference_number', 'receipt_number', 'lease__tenant__first_name')
    raw_id_fields = ('lease',)


@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ('apartment', 'title', 'category', 'priority', 'status', 'assigned_to_name', 'created_at')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('title', 'apartment__property__name', 'apartment__unit_number')
    raw_id_fields = ('apartment', 'tenant', 'assigned_to')


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('property', 'category', 'amount', 'expense_date', 'vendor', 'receipt_number')
    list_filter = ('category', 'property')
    search_fields = ('description', 'vendor', 'receipt_number')
    raw_id_fields = ('property', 'approved_by')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('report_type', 'property', 'start_date', 'end_date', 'total_income', 'total_expenses', 'net_income', 'created_at')
    list_filter = ('report_type', 'property')
    search_fields = ('property__name',)
    raw_id_fields = ('property', 'generated_by')


# Re-register User admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
