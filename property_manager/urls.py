"""
URL configuration for Property Manager project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apartments.views import super_admin_dashboard

urlpatterns = [
    # Major Admin Panel (hidden from website navigation)
    path('majoradmin/', include('majoradmin.urls')),
    
    # Super admin dashboard BEFORE admin.urls to avoid catch-all
    path('admin/super/', super_admin_dashboard, name='super_admin'),
    path('admin/', admin.site.urls),
    path('', include('apartments.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom Error Handlers
handler404 = 'django.views.defaults.page_not_found'
handler500 = 'django.views.defaults.server_error'
