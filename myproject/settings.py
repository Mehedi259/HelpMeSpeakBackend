import os
from pathlib import Path
from datetime import timedelta
import environ
import dj_database_url

# ------------------------------
# Base directory
# ------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------
# Load environment variables
# ------------------------------
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ["*"]),
    EMAIL_PORT=(int, 587),
    EMAIL_USE_TLS=(bool, True)
)

# Conditional load of .env file (optional for local)
env_file = os.path.join(BASE_DIR, ".env")
if os.path.exists(env_file):
    print(f".env file found at {env_file}, loading it...")
    environ.Env.read_env(env_file)
else:
    print(".env file not found, using system environment variables")

# ------------------------------
# Core settings
# ------------------------------
SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = [
    "127.0.0.1",       # লোকালহোস্ট
    "localhost",       # লোকালহোস্টের অন্য রূপ
    "10.10.7.116"      # আপনার লোকাল নেটওয়ার্ক আইপি (আপনার ইন্টারফেস অনুযায়ী)
]

GOOGLE_API_KEY = env("GOOGLE_API_KEY", default="")

# ------------------------------
# Installed apps
# ------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",   # ✅ এটা অবশ্যই লাগবে
    "dj_rest_auth",               # ✅ auth endpoints
    "dj_rest_auth.registration",  # ✅ allauth এর সাথে registration

    "authentication",
    "payment",
    "tts_app",
    "bot",
    "dashboard",

    "rest_framework_simplejwt",   # যদি JWT ও রাখতে চান

    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    
]


# ------------------------------
# Middleware
# ------------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # ✅ Added (must be on top)
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",  # ✅ Added for allauth
]

# ------------------------------
# URLs & WSGI
# ------------------------------
ROOT_URLCONF = "myproject.urls"
WSGI_APPLICATION = "myproject.wsgi.application"
AUTH_USER_MODEL = "authentication.User"

# ------------------------------
# Templates
# ------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",  # ✅ Required for allauth
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ------------------------------
# Database
# ------------------------------
DATABASES = {
    "default": dj_database_url.config(
        default=env("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
        conn_max_age=600,
    )
}

# ------------------------------
# REST Framework
# ------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

# ------------------------------
# JWT Settings
# ------------------------------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=100),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ------------------------------
# Email configuration
# ------------------------------
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")

# ------------------------------
# Static & Media
# ------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ------------------------------
# Localization
# ------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ------------------------------
# CORS Settings
# ------------------------------
CORS_ALLOW_ALL_ORIGINS = True   # ✅ Allow all origins (development use)

# ------------------------------
# django-allauth Settings
# ------------------------------
SITE_ID = 1  # ✅ Added, ensure a Site object exists with this ID
SOCIALACCOUNT_PROVIDERS = {  # ✅ Added for Google login
    'google': {
        'APP': {
            'client_id': env("GOOGLE_CLIENT_ID", default=""),
            'secret': env("GOOGLE_SECRET", default=""),
            'key': ''
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
            'prompt': 'select_account',
        }
    }
}

LOGIN_URL = 'login'  # ✅ Added
LOGOUT_URL = 'logout'  # ✅ Added
LOGIN_REDIRECT_URL = 'home'  # ✅ Added
SOCIALACCOUNT_LOGIN_ON_GET = True  # ✅ Added

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}