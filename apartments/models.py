"""
Database models for Apartment Management System
Property Manager - KIMATHI JORAM
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save


class UserProfile(models.Model):
    """Extended user profile with roles"""
    ROLE_CHOICES = [
        ('admin', 'System Administrator'),
        ('owner', 'Property Owner'),
        ('manager', 'Property Manager'),
        ('accountant', 'Accountant / Finance Officer'),
        ('maintenance', 'Maintenance Staff'),
        ('security', 'Security / Gate Officer'),
        ('tenant', 'Tenant'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='tenant')
    phone = models.CharField(max_length=20, blank=True)
    national_id = models.CharField(max_length=20, blank=True, help_text="National ID/Passport")
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    county = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Professional details
    kra_pin = models.CharField(max_length=20, blank=True, help_text="KRA PIN (Kenya)")
    years_experience = models.IntegerField(default=0, blank=True)
    company_name = models.CharField(max_length=200, blank=True)
    license_number = models.CharField(max_length=100, blank=True)
    skill_type = models.CharField(max_length=100, blank=True, help_text="For maintenance: Plumber, Electrician, etc.")
    
    # Banking information
    bank_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    bank_branch = models.CharField(max_length=100, blank=True)
    mpesa_paybill = models.CharField(max_length=50, blank=True)
    mpesa_till = models.CharField(max_length=50, blank=True)
    
    # Access permissions - configurable by admin
    can_add_tenants = models.BooleanField(default=False, help_text="Can add new tenants")
    can_approve_payments = models.BooleanField(default=False, help_text="Can approve payments")
    can_view_reports = models.BooleanField(default=False, help_text="Can view financial reports")
    can_create_lease = models.BooleanField(default=False, help_text="Can create lease agreements")
    can_create_payment = models.BooleanField(default=False, help_text="Can record payments")
    can_create_maintenance = models.BooleanField(default=False, help_text="Can create maintenance requests")
    can_manage_properties = models.BooleanField(default=False, help_text="Can add/edit properties")
    can_manage_apartments = models.BooleanField(default=False, help_text="Can add/edit apartments")
    can_manage_users = models.BooleanField(default=False, help_text="Can manage user accounts")
    can_view_all_payments = models.BooleanField(default=False, help_text="Can view all payment records")
    can_view_all_maintenance = models.BooleanField(default=False, help_text="Can view all maintenance requests")
    
    # Work details
    assigned_property = models.ForeignKey('Property', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_staff')
    availability_status = models.CharField(max_length=20, choices=[
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('off', 'Off Duty'),
    ], default='available')
    shift = models.CharField(max_length=20, choices=[
        ('day', 'Day'),
        ('night', 'Night'),
    ], blank=True)
    supervisor_name = models.CharField(max_length=200, blank=True)
    assigned_gate = models.CharField(max_length=50, blank=True)
    
    # Emergency contact
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_relation = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.get_role_display()}"
    
    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create user profile when user is created"""
    if created:
        UserProfile.objects.get_or_create(user=instance)


class Notification(models.Model):
    """Notifications for users"""
    NOTIFICATION_TYPES = [
        ('payment', 'Payment'),
        ('lease', 'Lease'),
        ('maintenance', 'Maintenance'),
        ('expense', 'Expense'),
        ('tenant', 'Tenant'),
        ('system', 'System'),
        ('announcement', 'Announcement'),
        ('social', 'Social Media'),
    ]
    
    TARGET_AUDIENCE = [
        ('all', 'All Users'),
        ('tenants', 'Tenants Only'),
        ('owners', 'Property Owners'),
        ('staff', 'Staff Members'),
        ('specific', 'Specific User'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    recipient_username = models.CharField(max_length=150, blank=True, help_text="Username if target is specific user")
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    target_audience = models.CharField(max_length=20, choices=TARGET_AUDIENCE, default='all')
    title = models.CharField(max_length=200)
    message = models.TextField()
    description = models.TextField(blank=True, help_text="Detailed description")
    link = models.CharField(max_length=500, blank=True, help_text="Main link (e.g., Google form)")
    image_url = models.URLField(max_length=500, blank=True, help_text="Image URL (e.g., from GitHub)")
    social_links = models.JSONField(default=dict, blank=True, help_text="Social media links as JSON: {'facebook': 'url', 'twitter': 'url', 'instagram': 'url', 'linkedin': 'url', 'youtube': 'url', 'tiktok': 'url', 'whatsapp': 'url'}")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username if self.recipient else 'Broadcast'}"


class Property(models.Model):
    """Model representing a property/building with apartments"""
    PROPERTY_TYPES = [
        ('apartment', 'Apartment Building'),
        ('bedsitter', 'Bedsitter'),
        ('commercial', 'Commercial Building'),
        ('land', 'Land'),
        ('villa', 'Villa'),
        ('house', 'House'),
    ]
    
    name = models.CharField(max_length=200, help_text="Property name or building name")
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES, default='apartment')
    address = models.TextField(help_text="Full address of the property")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="GPS Latitude coordinate")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="GPS Longitude coordinate")
    total_units = models.IntegerField(default=1, help_text="Total number of apartments/units")
    description = models.TextField(blank=True, help_text="Additional description")
    
    # Property documents
    title_deed_number = models.CharField(max_length=100, blank=True)
    water_account = models.CharField(max_length=50, blank=True)
    electricity_account = models.CharField(max_length=50, blank=True)
    
    # Owner information
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_properties')
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def available_units(self):
        """Calculate available units"""
        occupied = self.apartments.filter(leases__status='active').distinct().count()
        return self.total_units - occupied


class Apartment(models.Model):
    """Model representing individual apartment/unit"""
    APARTMENT_TYPES = [
        ('studio', 'Studio'),
        ('one_bed', '1 Bedroom'),
        ('two_bed', '2 Bedroom'),
        ('three_bed', '3 Bedroom'),
        ('four_bed', '4 Bedroom'),
        ('penthouse', 'Penthouse'),
        ('bedsitter', 'Bedsitter'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Under Maintenance'),
        ('reserved', 'Reserved'),
    ]
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='apartments')
    unit_number = models.CharField(max_length=50, help_text="Unit/Apartment number")
    floor = models.IntegerField(default=1, help_text="Floor number")
    apartment_type = models.CharField(max_length=20, choices=APARTMENT_TYPES, default='one_bed', db_index=True)
    bedrooms = models.IntegerField(default=1)
    bathrooms = models.FloatField(default=1.0)
    area_sqft = models.FloatField(default=0, help_text="Area in square feet")
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Monthly rent")
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Security deposit")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', db_index=True)
    description = models.TextField(blank=True)
    
    # Features
    has_water = models.BooleanField(default=True)
    has_electricity = models.BooleanField(default=True)
    has_wifi = models.BooleanField(default=False)
    has_parking = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['property', 'unit_number']
        unique_together = ['property', 'unit_number']
        indexes = [
            models.Index(fields=['property', 'status']),
            models.Index(fields=['apartment_type']),
        ]
    
    def __str__(self):
        return f"{self.property.name} - Unit {self.unit_number}"


class Tenant(models.Model):
    """Model representing a tenant/renter"""
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='tenant_profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, db_index=True)
    phone = models.CharField(max_length=20, db_index=True)
    alternative_phone = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male', db_index=True)
    id_number = models.CharField(max_length=20, help_text="National ID/Passport number", db_index=True)
    date_of_birth = models.DateField(null=True, blank=True)
    occupation = models.CharField(max_length=200, blank=True)
    employer = models.CharField(max_length=200, blank=True)
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    employer_contact = models.CharField(max_length=200, blank=True)
    
    # Next of kin
    next_of_kin_name = models.CharField(max_length=200, blank=True)
    next_of_kin_contact = models.CharField(max_length=20, blank=True)
    
    # Documents
    id_copy = models.ImageField(upload_to='tenants/ids/', blank=True, null=True)
    lease_agreement = models.FileField(upload_to='tenants/leases/', blank=True, null=True)
    photo = models.ImageField(upload_to='tenants/', blank=True, null=True)
    
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['last_name', 'first_name']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Lease(models.Model):
    """Model representing lease agreement"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('terminated', 'Terminated'),
        ('pending', 'Pending'),
    ]
    
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name='leases', db_index=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='leases', db_index=True)
    start_date = models.DateField(help_text="Lease start date", db_index=True)
    end_date = models.DateField(help_text="Lease end date", db_index=True)
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Monthly rent")
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Security deposit")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    terms = models.TextField(blank=True, help_text="Lease terms and conditions")
    
    # Auto-renewal
    auto_renew = models.BooleanField(default=False)
    notice_period_days = models.IntegerField(default=30)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.apartment} - {self.tenant} ({self.start_date} to {self.end_date})"
    
    @property
    def is_active(self):
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date and self.status == 'active'
    
    @property
    def days_remaining(self):
        if not self.is_active:
            return 0
        today = timezone.now().date()
        return (self.end_date - today).days


class Payment(models.Model):
    """Model representing rent payments"""
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('mpesa', 'M-Pesa'),
        ('cheque', 'Cheque'),
        ('card', 'Card'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='payments', db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=timezone.now, db_index=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash', db_index=True)
    reference_number = models.CharField(max_length=100, blank=True, help_text="Transaction reference")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    notes = models.TextField(blank=True)
    
    # Receipt
    receipt_number = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['-payment_date']),
            models.Index(fields=['status', 'payment_date']),
        ]
    
    def __str__(self):
        return f"Payment {self.amount} for {self.lease} on {self.payment_date}"


class MaintenanceRequest(models.Model):
    """Model representing maintenance requests"""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('emergency', 'Emergency'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    CATEGORY_CHOICES = [
        ('plumbing', 'Plumbing'),
        ('electrical', 'Electrical'),
        ('carpentry', 'Carpentry'),
        ('painting', 'Painting'),
        ('appliances', 'Appliances'),
        ('hvac', 'HVAC'),
        ('pest_control', 'Pest Control'),
        ('other', 'Other'),
    ]
    
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name='maintenance_requests', db_index=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenance_requests')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other', db_index=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_maintenance')
    assigned_to_name = models.CharField(max_length=200, blank=True, help_text="Contractor or staff assigned")
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    scheduled_date = models.DateField(null=True, blank=True, db_index=True)
    completed_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    # Before/after images
    before_image = models.ImageField(upload_to='maintenance/before/', blank=True, null=True)
    after_image = models.ImageField(upload_to='maintenance/after/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status', 'priority']),
        ]
    
    def __str__(self):
        return f"{self.apartment} - {self.title}"


class Expense(models.Model):
    """Model representing property expenses"""
    CATEGORY_CHOICES = [
        ('repairs', 'Repairs'),
        ('maintenance', 'Maintenance'),
        ('utilities', 'Utilities'),
        ('insurance', 'Insurance'),
        ('taxes', 'Taxes'),
        ('management', 'Management Fee'),
        ('security', 'Security'),
        ('cleaning', 'Cleaning'),
        ('landscaping', 'Landscaping'),
        ('other', 'Other'),
    ]
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='expenses', db_index=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other', db_index=True)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expense_date = models.DateField(default=timezone.now, db_index=True)
    vendor = models.CharField(max_length=200, blank=True)
    receipt_number = models.CharField(max_length=100, blank=True)
    receipt_image = models.ImageField(upload_to='expenses/receipts/', blank=True, null=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_expenses')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-expense_date']
        indexes = [
            models.Index(fields=['-expense_date']),
            models.Index(fields=['category', 'expense_date']),
        ]
    
    def __str__(self):
        return f"{self.property.name} - {self.category} - {self.amount}"


class Report(models.Model):
    """Model for storing generated reports"""
    REPORT_TYPES = [
        ('income', 'Income Report'),
        ('occupancy', 'Occupancy Report'),
        ('maintenance', 'Maintenance Report'),
        ('financial', 'Financial Report'),
        ('tenant', 'Tenant Report'),
        ('expense', 'Expense Report'),
    ]
    
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    start_date = models.DateField()
    end_date = models.DateField()
    total_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    data = models.JSONField(default=dict, help_text="Report data in JSON format")
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.start_date} to {self.end_date}"
