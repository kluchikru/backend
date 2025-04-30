from pathlib import Path
from datetime import timedelta
from decouple import config, Csv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-qm62lfi_za5v5tr)*3jocz$rx$j34gf44q4x$)b5$o-jo)r_#m"

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
    "rest_framework",  # Создание API
    "rest_framework_simplejwt.token_blacklist",  # Чтобы хранить JWT в cookie
    "corsheaders",  # Чтобы не было ошибки CORS при запросах с F на B
    "kluchik",  # Мое приложение B
    "djoser",  # Для получения авторизационного токена для custom model Vue+DRF
]

# Авторизация через JWT DRF
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        # "kluchik.authentication.CookieJWTAuthentication",
    ],
}

# Структура JWT
SIMPLE_JWT = {
    "AUTH_COOKIE": "access_token",  # имя куки
    "AUTH_COOKIE_REFRESH": "refresh_token",  # имя токена
    "AUTH_COOKIE_HTTP_ONLY": True,  # запрет доступа из JS
    "AUTH_COOKIE_SECURE": False,  # Нужно False для HTTP на локальном сервере
    "AUTH_COOKIE_PATH": "/",
    "AUTH_COOKIE_SAMESITE": "None",  # Используй Lax или Strict на локальной разработке
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}


# Информация по авторизации
DJOSER = {
    "PASSWORD_RESET_CONFIRM_URL": "password-reset-confirm/{uid}/{token}",
    "LOGIN_FIELD": "email",
    "USER_ID_FIELD": "id",
    "SERIALIZERS": {
        "token_create": "kluchik.serializers.CustomTokenObtainPairSerializer",
        "user_create": "kluchik.serializers.UserCreateSerializer",
        "user": "kluchik.serializers.UserSerializer",
        "current_user": "kluchik.serializers.UserSerializer",
    },
}
# Список URL, которые могут получить доступ к Backend
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

# Срок для токена восстановление пароля
PASSWORD_RESET_TIMEOUT = 60 * 30  # 30 минут

# Данные для почтовой рассылки
DOMAIN = "127.0.0.1:8080"
SITE_NAME = "http://localhost:8080"
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

MIDDLEWARE = [
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# Cookie
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "project.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Переназначение User Auth Model
AUTH_USER_MODEL = "kluchik.User"

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

# Интерфейс DA на русском
LANGUAGE_CODE = "ru"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
