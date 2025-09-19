# PERFORMANCE OPTIMIZATION SETTINGS
# Add these to your Django settings.py for maximum performance

# Database Connection Pooling
DATABASES = {
    'default': {
        # ... your existing database config ...
        'CONN_MAX_AGE': 60,  # Connection pooling
        'OPTIONS': {
            'MAX_CONNS': 20,  # Maximum connections
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}

# Caching for RFID lookups (optional but recommended)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'access-control-cache',
        'TIMEOUT': 300,  # 5 minutes
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# Logging optimization for production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'access_file': {
            'level': 'WARNING',  # Only log warnings and errors in production
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/access_control.log',
            'maxBytes': 1024*1024,  # 1MB
            'backupCount': 3,
        },
    },
    'loggers': {
        'access': {
            'handlers': ['access_file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Database query optimization
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Session and CSRF optimization for API endpoints
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
USE_TZ = True