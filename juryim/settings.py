"""
Django settings for juryim project.

Generated by 'django-admin startproject' using Django 4.2.17.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-f94qn*29m+r4yj_qsac#6j7f+db9!c1-bqi3m%$m)m+0tdv4pi"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Add our apps
    "users",
    "financial",
    "gambling",
    "tasks",
    "groups",
    "user_notifications",
    # Add required third-party apps
    "rest_framework",
    "channels",
    "corsheaders",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'users.middleware.IPTrackingMiddleware',
]

ROOT_URLCONF = "juryim.urls"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'juryim' / 'templates',
            BASE_DIR / 'financial' / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = "juryim.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Add this line to specify the custom user model
AUTH_USER_MODEL = 'users.User'

# Update login URL to use your custom login view
LOGIN_URL = 'users:login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'users:login'

# Add channel layers configuration
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

# Update ASGI application
ASGI_APPLICATION = 'juryim.routing.application'

# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Celery Beat Schedule
CELERY_BEAT_SCHEDULE = {
    'check_deposit_confirmations': {
        'task': 'financial.tasks.check_deposit_confirmations',
        'schedule': 60.0,  # Run every 60 seconds
    },
    'process_withdrawals': {
        'task': 'financial.tasks.process_pending_withdrawals',
        'schedule': 60.0,  # Run every 60 seconds
    },
    'monitor_system': {
        'task': 'financial.tasks.monitor_system',
        'schedule': 300.0,  # Run every 5 minutes
    },
}

# Blockchain API Settings
BITCOIN_RPC_URL = 'http://username:password@localhost:8332'
ETH_CHAIN_ID = 1  # 1 for mainnet, 3 for ropsten, etc.
ETH_WALLET_ADDRESS = 'YOUR_ETH_WALLET_ADDRESS'
ETH_PRIVATE_KEY = 'YOUR_ETH_PRIVATE_KEY'
ETHEREUM_RPC_URL = 'https://mainnet.infura.io/v3/YOUR_PROJECT_ID'

# USDT Contract Settings (TRC20)
TRON_API_URL = 'https://api.trongrid.io'
TRON_WALLET_ADDRESS = 'YOUR_TRON_WALLET_ADDRESS'
USDT_CONTRACT_ADDRESS = 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t'  # USDT TRC20 contract

# Network Settings
NETWORK_SETTINGS = {
    'BTC': {
        'confirmations_required': 3,
        'min_withdrawal': '0.001',
        'max_withdrawal': '10.0',
        'withdrawal_fee': '0.0001',
    },
    'ETH': {
        'confirmations_required': 12,
        'min_withdrawal': '0.01',
        'max_withdrawal': '100.0',
        'withdrawal_fee': '0.001',
    },
    'USDT': {
        'confirmations_required': 20,
        'min_withdrawal': '10.0',
        'max_withdrawal': '100000.0',
        'withdrawal_fee': '1.0',
    }
}

# Email Settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Update with your SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'pekdream2013@gmail.com'  # Update with your email
EMAIL_HOST_USER_PASSWORD = 'just&go_6530'  # Update with your password
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Notification Settings
WITHDRAWAL_NOTIFICATIONS = True
ADMIN_EMAIL = 'admin@example.com'

# Override settings with local configuration if it exists
try:
    from .local_settings import *
except ImportError:
    pass

# Validate required settings
REQUIRED_SETTINGS = [
    'BITCOIN_RPC_URL',
    'ETH_WALLET_ADDRESS',
    'ETH_PRIVATE_KEY',
    'ETHEREUM_RPC_URL',
    'TRON_WALLET_ADDRESS',
]

for setting in REQUIRED_SETTINGS:
    if not globals().get(setting):
        raise ValueError(f"Missing required setting: {setting}")

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/blockchain.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'blockchain': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Remove these authentication backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Keep only this one
]
