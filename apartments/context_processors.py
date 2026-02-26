"""Context processors for apartments app"""
from django.db.models import Q, Sum


def notification_count(request):
    """Add unread notification count to all templates"""
    from apartments.models import Notification, UserProfile
    
    unread_count = 0
    
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            user_role = profile.role if profile else None
            
            # Get notifications for this user or broadcast
            notifications = Notification.objects.filter(
                Q(recipient=request.user) | Q(recipient=None)
            )
            
            # Filter based on audience
            user_notifications = []
            for notif in notifications:
                if notif.recipient is not None and notif.recipient == request.user:
                    user_notifications.append(notif)
                elif notif.recipient is None:
                    if notif.target_audience == 'all':
                        user_notifications.append(notif)
                    elif notif.target_audience == 'tenants' and user_role == 'tenant':
                        user_notifications.append(notif)
                    elif notif.target_audience == 'owners' and user_role == 'owner':
                        user_notifications.append(notif)
                    elif notif.target_audience == 'staff' and (request.user.is_staff or request.user.is_superuser):
                        user_notifications.append(notif)
            
            unread_count = sum(1 for n in user_notifications if not n.is_read)
        except Exception:
            pass
    
    return {'unread_notification_count': unread_count}


def payment_count(request):
    """Add payment counts to all templates"""
    from apartments.models import Payment, Lease
    
    pending_payments_count = 0
    my_payments_count = 0
    total_payments_amount = 0
    
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            user_role = profile.role if profile else None
            
            if user_role == 'tenant':
                # For tenants, show their pending payments
                leases = Lease.objects.filter(tenant=request.user, status='active')
                my_payments = Payment.objects.filter(
                    lease__in=leases,
                    status='pending'
                )
                pending_payments_count = my_payments.count()
                my_payments_count = Payment.objects.filter(lease__in=leases).count()
                
            elif user_role in ['owner', 'accountant', 'admin'] or request.user.is_staff:
                # For staff/owners, show all pending payments
                pending_payments_count = Payment.objects.filter(status='pending').count()
                my_payments_count = Payment.objects.filter(status='completed').count()
                total_payments_amount = Payment.objects.filter(
                    status='completed'
                ).aggregate(total=Sum('amount'))['total'] or 0
            
        except Exception:
            pass
    
    return {
        'pending_payments_count': pending_payments_count,
        'my_payments_count': my_payments_count,
        'total_payments_amount': total_payments_amount,
    }
