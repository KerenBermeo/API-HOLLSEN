import locale
from pathlib import Path
from decouple import config
import dj_database_url
import sys
#from api.models.users.models_users import User

REQUIRED_ENV_VARS = ['SECRET_KEY', 'DATABASE_URL']

missing_vars = [var for var in REQUIRED_ENV_VARS if not config(var, default=None)]

if missing_vars:
    print(f"Error: Las siguientes variables de entorno son requeridas pero no están configuradas: {', '.join(missing_vars)}")
    sys.exit(1)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-6q=n!md0fk)$v&77-lmcm%mm3ucva31@*mp@b8inpl@zj!qi7w')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

# Configuración personalizada para el modelo de usuario
#AUTH_USER_MODEL = 'api.User' 

# Application definition

INSTALLED_APPS = [
    # Django core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps (cada una solo una vez)
    'rest_framework',
    'corsheaders',
    'rest_framework_simplejwt.token_blacklist',  # Incluye funcionalidad de rest_framework_simplejwt
    
    'api',
]

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'utils.renderers.CustomJSONRenderer',  # Renderizador personalizado 
    ],
    'EXCEPTION_HANDLER': 'utils.exceptions.custom_exception_handler',  # Manejador de excepciones personalizado
    'DEFAULT_PAGINATION_CLASS': 'utils.pagination.StandardResultsSetPagination', # Configuración de paginación global
    'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',  
    ],
}


from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=12),  # Duración más larga para trabajar offline
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),   # Permite refrescar después de reconectarse
    'ROTATE_REFRESH_TOKENS': False,               # Desactivado para evitar problemas offline
    'BLACKLIST_AFTER_ROTATION': True,             # Blacklist si decides rotar manualmente
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'api.middlewares.CustomExceptionMiddleware',
]

# Configuración de CORS
CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL_ORIGINS', default=True, cast=bool)
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='').split(',') if config('CORS_ALLOWED_ORIGINS', default='') else []
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]

ROOT_URLCONF = 'ecommerce_api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'LibroMayor.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
DATABASE_URL = config('DATABASE_URL', default='sqlite:///db.sqlite3')
DATABASES = {
    'default': dj_database_url.config(default=DATABASE_URL)
}




# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/
# Codificación por defecto
LANGUAGE_CODE = 'es-co'  # Español colombiano
TIME_ZONE = 'America/Bogota'  # Zona horaria de Bogotá
USE_I18N = True  # Internacionalización
USE_L10N = True  # Localización
USE_TZ = True   # Usar zona horaria


# --- Configuración de locale con manejo de errores ---
# Define locales a probar (en orden de preferencia)
DEFAULT_LOCALES = [
    config('DJANGO_LOCALE', default='es_CO.UTF-8'),  # Variable de entorno
    'es_CO.UTF-8',  # Opción preferida
    'es_ES.UTF-8',  # Alternativa
    'en_US.UTF-8',  # Locale común en servidores
    'C.UTF-8',      # Locale mínima garantizada
]

# Intenta configurar la primera locale disponible
for loc in DEFAULT_LOCALES:
    try:
        locale.setlocale(locale.LC_ALL, loc)
        break  # Si funciona, sal del bucle
    except locale.Error:
        continue  # Si falla, prueba la siguiente



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}