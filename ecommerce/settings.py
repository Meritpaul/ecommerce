"""
Django settings for PureShop ecommerce project.
Production-ready configuration with environment variables.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# SECURITY
# ==============================================================================

SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-in-production')

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')

# ==============================================================================
# INSTALLED APPS
# ==============================================================================

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    # Project apps
    'products',
    'cart',
    'orders',
    'accounts',
]

# ==============================================================================
# MIDDLEWARE
# ==============================================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',     # Static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ecommerce.urls'

# ==============================================================================
# TEMPLATES
# ==============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'products.context_processors.categories',
                'orders.context_processors.sales_data',
            ],
        },
    },
]

WSGI_APPLICATION = 'ecommerce.wsgi.application'

# ==============================================================================
# DATABASE
# ==============================================================================

# Uses DATABASE_URL env var if set (PostgreSQL for production),
# falls back to SQLite for local development
DATABASE_URL = os.environ.get('DATABASE_URL', '')

if DATABASE_URL:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=not DEBUG,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ==============================================================================
# PASSWORD VALIDATION
# ==============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==============================================================================
# INTERNATIONALIZATION
# ==============================================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Dhaka'
USE_I18N = True
USE_TZ = True

# ==============================================================================
# STATIC & MEDIA FILES
# ==============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# WhiteNoise compressed static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ==============================================================================
# AUTH REDIRECTS
# ==============================================================================

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# ==============================================================================
# PAYMENT GATEWAY (SSLCommerz)
# ==============================================================================

SSLCOMMERZ_STORE_ID   = os.environ.get('SSLCOMMERZ_STORE_ID', 'testbox')
SSLCOMMERZ_STORE_PASS = os.environ.get('SSLCOMMERZ_STORE_PASS', 'qwerty')
SITE_URL              = os.environ.get('SITE_URL', 'http://127.0.0.1:8000')

# Sandbox in DEBUG, live in production
SSLCOMMERZ_API_URL = (
    'https://sandbox.sslcommerz.com/gwprocess/v4/api.php'
    if DEBUG else
    'https://securepay.sslcommerz.com/gwprocess/v4/api.php'
)

# ==============================================================================
# SECURITY HEADERS (only in production)
# ==============================================================================

if not DEBUG:
    SECURE_SSL_REDIRECT              = True
    SECURE_HSTS_SECONDS              = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS   = True
    SECURE_HSTS_PRELOAD              = True
    SESSION_COOKIE_SECURE            = True
    CSRF_COOKIE_SECURE               = True
    SECURE_CONTENT_TYPE_NOSNIFF      = True
    SECURE_BROWSER_XSS_FILTER        = True
    X_FRAME_OPTIONS                  = 'DENY'

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY    = True

# ==============================================================================
# CACHING (local memory; swap for Redis in production)
# ==============================================================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'pureshop-cache',
    }
}

# ==============================================================================
# LOGGING
# ==============================================================================

LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} — {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'django.log'),
            'maxBytes': 1024 * 1024 * 5,   # 5 MB
            'backupCount': 3,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'WARNING'),
            'propagate': False,
        },
    },
}

# ==============================================================================
# DEFAULT AUTO FIELD
# ==============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================================================================
# STORE CONSTANTS
# ==============================================================================

FREE_DELIVERY_THRESHOLD = 500   # TK — orders above this get free delivery
DELIVERY_CHARGE         = 60    # TK — flat delivery charge below threshold

# ==============================================================================
# JAZZMIN ADMIN THEME
# ==============================================================================

JAZZMIN_SETTINGS = {
    # Branding
    "site_title": "PureShop Admin",
    "site_header": "PureShop",
    "site_brand": "🌿 PureShop",
    "site_logo": None,
    "login_logo": None,
    "site_logo_classes": "img-circle",
    "site_icon": None,
    "welcome_sign": "Welcome to PureShop Admin Panel",
    "copyright": "PureShop",

    # Search bar — model to search by default
    "search_model": ["products.Product", "orders.Order"],

    # User menu on the right
    "user_avatar": None,

    # Top Menu
    "topmenu_links": [
        {"name": "🏠 Visit Site", "url": "/", "new_window": True},
        {"model": "products.Product"},
        {"model": "orders.Order"},
        {"app": "products"},
    ],

    # Side Menu
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],

    # Order apps/models in sidebar
    "order_with_respect_to": [
        "products",
        "products.Product",
        "products.Category",
        "products.Banner",
        "products.Wishlist",
        "orders",
        "orders.Order",
        "orders.OrderItem",
        "accounts",
        "auth",
    ],

    # Icons (Font Awesome 5)
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "accounts.UserProfile": "fas fa-id-card",
        "products.Product": "fas fa-box-open",
        "products.Category": "fas fa-tags",
        "products.Banner": "fas fa-images",
        "products.Wishlist": "fas fa-heart",
        "orders.Order": "fas fa-receipt",
        "orders.OrderItem": "fas fa-list",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    # UI tweaks
    "related_modal_active": True,
    "custom_css": None,
    "custom_js": None,
    "show_ui_builder": False,

    # Change form layout
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "products.product": "collapsible",
        "orders.order": "horizontal_tabs",
    },
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-warning",
    "accent": "accent-warning",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-light-warning",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "default_theme_mode": "light",
    "button_classes": {
        "primary": "btn-warning",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
    "actions_sticky_top": True,
}