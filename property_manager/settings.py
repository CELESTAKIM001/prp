"""
Django settings for Property Manager project.
Apartment Management System for KIMATHI JORAM
"""

import os
from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-kimathi-joram-apartment-manager-2024')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'jazzmin',
    'apartments',
    'majoradmin',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'property_manager.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apartments.context_processors.notification_count',
                'apartments.context_processors.payment_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'property_manager.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# Login URL
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# Jazzmin Settings - Modern Django Admin
JAZZMIN_SETTINGS = {
    # title of the window
    "site_title": "Property Manager Admin",
    
    # Title on the login screen
    "site_header": "KIMATHI JORAM Properties",
    
    # Title on the brand
    "site_brand": "KIMATHI JORAM",
    
    # Logo to use for your site (Font Awesome class)
    "site_logo": "fas fa-building",
    
    # CSS classes that are applied to the logo
    "site_logo_classes": "",
    
    # Welcome text on the login screen
    "welcome_sign": "Welcome to Property Manager",
    
    # Copyright on the footer
    "copyright": "© 2026 KIMATHI JORAM Properties",
    
    # List of model admins to search from the search bar
    "search_model": ["auth.User", "auth.Group"],
    
    # Field name on user model that contains avatar
    "user_avatar": None,
    
    ############
    # Top Menu #
    ############
    
    # Links to put along the top menu
    "topmenu_links": [
        # Url that gets reversed
        {"name": "Home", "url": "/", "icon": "fas fa-home"},
        # External url that opens in a new window
        {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
        # App with dropdown menu to all its models pages
        {"app": "apartments"},
    ],
    
    #############
    # User Menu #
    #############
    
    # Additional links to include in the user menu
    "usermenu_links": [
        {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
    ],
    
    #############
    # Side Menu #
    #############
    
    # Whether to display the side menu
    "show_sidebar": True,
    
    # Whether to aut expand the menu
    "navigation_expanded": True,
    
    # Hide these apps when generating side menu
    "hide_apps": [],
    
    # Hide these models when generating side menu
    "hide_models": [],
    
    # Custom links to append to app groups
    "custom_links": {
        "apartments": [
            {"name": "Dashboard", "url": "dashboard", "icon": "fas fa-tachometer-alt"}
        ]
    },
    
    # Custom icons for side menu apps/models
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.User": "fas fa-user-circle",
        "auth.Group": "fas fa-user-shield",
        "auth.Permission": "fas fa-shield-alt",
        "apartments.Property": "fas fa-city",
        "apartments.Apartment": "fas fa-building",
        "apartments.Tenant": "fas fa-user-tie",
        "apartments.Lease": "fas fa-file-signature",
        "apartments.Payment": "fas fa-credit-card",
        "apartments.Expense": "fas fa-file-invoice-dollar",
        "apartments.Maintenance": "fas fa-hard-hat",
        "apartments.Notification": "fas fa-bell",
        "apartments.UserProfile": "fas fa-id-card",
    },
    
    # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-folder-open",
    "default_icon_children": "fas fa-file",
    
    #################
    # Related Modal #
    #################
    # Use modals instead of popups
    "related_modal_active": True,
    
    #############
    # UI Tweaks #
    #############
    
    # Custom CSS for modern styling - Bootstrap 5, Tailwind, Google Fonts, Font Awesome
    "custom_css": """
        /* Import Google Fonts - Inter */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Base Font Family */
        body, .main-header, .sidebar, .nav-sidebar, .card-header, .table thead th {
            font-family: 'Inter', sans-serif !important;
        }
        
        /* Modern Card Styling */
        .card { 
            border-radius: 12px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
            border: none; 
            overflow: hidden;
        }
        .card-header { 
            border-radius: 12px 12px 0 0 !important; 
            font-weight: 600; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            border: none;
            padding: 15px 20px;
        }
        .card-body { padding: 20px; }
        
        /* Modern Table Styling */
        .table { 
            border-radius: 8px; 
            overflow: hidden; 
            margin-bottom: 0;
        }
        .table thead th { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            font-weight: 600; 
            border: none; 
            padding: 14px 12px;
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.5px;
        }
        .table tbody tr { 
            transition: all 0.2s ease;
        }
        .table tbody tr:hover { 
            background-color: rgba(102, 126, 234, 0.1); 
            transform: scale(1.01);
        }
        .table tbody td {
            padding: 12px;
            vertical-align: middle;
            border-color: #e9ecef;
        }
        
        /* Modern Button Animations */
        .btn { 
            border-radius: 8px; 
            font-weight: 500; 
            transition: all 0.3s ease;
            padding: 8px 16px;
            border: none;
        }
        .btn:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .btn-success {
            background: linear-gradient(135deg, #00c853 0%, #009624 100%);
        }
        .btn-danger {
            background: linear-gradient(135deg, #ff5252 0%, #d32f2f 100%);
        }
        
        /* Sidebar Modern Styling */
        .main-sidebar { 
            box-shadow: 2px 0 10px rgba(0,0,0,0.1); 
            background: #1a1a2e;
        }
        .sidebar { background: #1a1a2e; }
        .nav-sidebar .nav-item > .nav-link { border-radius: 8px; margin: 2px 8px; }
        .nav-sidebar .nav-item .nav-link:hover { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            border-radius: 8px; 
        }
        .nav-sidebar .nav-item .nav-link.active { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 8px;
        }
        
        /* Modern Form Controls */
        .form-control, .form-select { 
            border-radius: 8px; 
            border: 2px solid #e0e0e0; 
            transition: all 0.3s ease; 
            padding: 10px 15px;
        }
        .form-control:focus, .form-select:focus { 
            border-color: #667eea; 
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
        }
        .form-label { font-weight: 500; color: #495057; }
        
        /* Admin Brand Logo */
        .brand-link { 
            border-bottom: 1px solid rgba(255,255,255,0.1); 
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .brand-text { font-weight: 700; font-size: 1.2rem; }
        
        /* User Panel */
        .user-panel { 
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding: 15px;
        }
        .user-panel .info { color: #fff; }
        .user-panel .info span { font-weight: 600; }
        
        /* Page Header */
        .content-header { 
            padding: 20px 0; 
            background: #f8f9fa;
            margin-bottom: 20px;
            border-bottom: 1px solid #dee2e6;
        }
        .content-header h1 { 
            font-weight: 700; 
            color: #333;
            font-size: 1.75rem;
        }
        
        /* Breadcrumb */
        .breadcrumb { 
            background: transparent; 
            padding: 0;
            margin-bottom: 0;
        }
        .breadcrumb-item a { color: #667eea; }
        .breadcrumb-item.active { color: #495057; }
        
        /* Pagination */
        .pagination .page-link { 
            border-radius: 8px; 
            margin: 0 3px; 
            border: none;
            color: #495057;
        }
        .pagination .page-item.active .page-link { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white;
        }
        .pagination .page-link:hover {
            background: #e9ecef;
        }
        
        /* Alert Messages */
        .alert { 
            border-radius: 10px; 
            border: none;
            padding: 15px 20px;
        }
        .alert-success { background: linear-gradient(135deg, #00c853 0%, #009624 100%); color: white; }
        .alert-danger { background: linear-gradient(135deg, #ff5252 0%, #d32f2f 100%); color: white; }
        .alert-warning { background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); color: white; }
        .alert-info { background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%); color: white; }
        
        /* Login Page */
        .login-card { 
            border-radius: 15px; 
            box-shadow: 0 10px 40px rgba(0,0,0,0.2); 
            overflow: hidden;
        }
        .login-header { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            border-radius: 15px 15px 0 0;
            padding: 30px;
        }
        .login-box { 
            min-height: 400px;
        }
        
        /* Admin Change List Actions */
        .actions { 
            background: #f8f9fa;
            padding: 10px;
            border-radius: 8px;
        }
        
        /* Filter Section */
        #changelist-filter {
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        .filter-horizontal ul { flex-wrap: wrap; }
        
        /* Search Bar */
        #searchbar {
            border-radius: 20px;
            padding-left: 15px;
            border: 2px solid #e9ecef;
        }
        #searchbar:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        /* Modal Styling */
        .modal-content {
            border-radius: 12px;
            border: none;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        .modal-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 12px 12px 0 0;
        }
        
        /* Toast Notifications */
        .toast {
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
    """,
    
    # Custom JS to include - Tailwind CSS CDN
    "custom_js": """
        // Load Tailwind CSS
        (function() {
            var tailwindScript = document.createElement('script');
            tailwindScript.src = 'https://cdn.tailwindcss.com';
            tailwindScript.onload = function() {
                // Configure Tailwind
                tailwind.config = {
                    theme: {
                        extend: {
                            fontFamily: {
                                sans: ['Inter', 'sans-serif'],
                            },
                            colors: {
                                primary: '#667eea',
                                secondary: '#764ba2',
                            }
                        }
                    }
                }
            };
            document.head.appendChild(tailwindScript);
        })();
        
        // Load Font Awesome 6
        (function() {
            var faScript = document.createElement('link');
            faScript.rel = 'stylesheet';
            faScript.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css';
            document.head.appendChild(faScript);
        })();
        
        // Add smooth scroll and animations
        document.addEventListener('DOMContentLoaded', function() {
            // Smooth transitions
            document.body.style.scrollBehavior = 'smooth';
            
            // Add animation classes to table rows
            var tableRows = document.querySelectorAll('#result_list tbody tr');
            tableRows.forEach(function(row, index) {
                row.style.animationDelay = (index * 0.05) + 's';
                row.classList.add('transition-all', 'duration-200');
            });
            
            // Enhance buttons
            var buttons = document.querySelectorAll('.btn');
            buttons.forEach(function(btn) {
                btn.classList.add('transition', 'transform', 'hover:-translate-y-0.5');
            });
        });
    """,
    
    # Whether to link font from fonts.googleapis.com
    "use_google_fonts_cdn": True,
    
    # Whether to show the UI customizer on the sidebar
    "show_ui_builder": True,
    
    ###############
    # Change view #
    ###############
    # Render out the change view as tabs
    "changeform_format": "horizontal_tabs",
    
    # Add a language dropdown into the admin
    "language_chooser": False,
    
    ############
    # UI Tweaks #
    ############
    "ui_tweaks": {
        "sidebar": "sidebar-dark-indigo",
        "theme": "dark",
        "dark_mode_theme": "cyborg",
        "button_classes": {
            "primary": "btn-primary",
            "secondary": "btn-secondary",
            "info": "btn-info",
            "success": "btn-success",
            "warning": "btn-warning",
            "danger": "btn-danger",
        },
        "navbar": "navbar-dark",
    },
    
    # Themes available for selection
    "themes": {
        "default": {"primary": "#677b8c", "secondary": "#677b8c"},
        "modern-purple": {"primary": "#667eea", "secondary": "#764ba2"},
        "modern-blue": {"primary": "#2196F3", "secondary": "#1976D2"},
        "modern-green": {"primary": "#00c853", "secondary": "#009624"},
        "modern-red": {"primary": "#ff5252", "secondary": "#d32f2f"},
        "dark": {"primary": "#3a3b45", "secondary": "#2c2e33"},
        "light": {"primary": "#007bff", "secondary": "#0056b3"},
    },
}

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
