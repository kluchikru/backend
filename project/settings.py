from pathlib import Path
from datetime import timedelta
from decouple import config
import os

# === Базовые настройки проекта ===

# Корневая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Внимание: храните секретный ключ в .env файле на продакшене!
SECRET_KEY = "django-insecure-qm62lfi_za5v5tr)*3jocz$rx$j34gf44q4x$)b5$o-jo)r_#m"

# Для загрузки медиафайлов
MEDIA_URL = "/media/"  # URL для доступа к медиафайлам
MEDIA_ROOT = os.path.join(BASE_DIR, "media")  # Папка, где будут храниться медиафайлы

# Включайте DEBUG только при локальной разработке
DEBUG = True

ALLOWED_HOSTS = []


# === Приложения ===

INSTALLED_APPS = [
    # Django-приложения
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Сторонние библиотеки
    "rest_framework",  # DRF: создание API
    "rest_framework_simplejwt.token_blacklist",  # Хранение JWT в cookie
    "corsheaders",  # Разрешение CORS-запросов
    "djoser",  # Аутентификация через email
    # Собственные приложения
    "kluchik",
]


# === Middleware ===

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


# === Конфигурация REST Framework ===

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "rest_framework.filters.SearchFilter",
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    # При необходимости можно включить авторизацию по умолчанию:
    # "DEFAULT_PERMISSION_CLASSES": [
    #     "rest_framework.permissions.IsAuthenticated",
    # ],
}


# === Настройки JWT ===

SIMPLE_JWT = {
    "AUTH_COOKIE": "access_token",
    "AUTH_COOKIE_REFRESH": "refresh_token",
    "AUTH_COOKIE_HTTP_ONLY": True,
    "AUTH_COOKIE_SECURE": False,  # Для разработки должно быть False
    "AUTH_COOKIE_PATH": "/",
    "AUTH_COOKIE_SAMESITE": "None",
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("JWT",),  # Важно: для работы с Djoser
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}


# === Настройки Djoser ===

DJOSER = {
    "SET_PASSWORD_RETYPE": True,
    "SET_USERNAME_RETYPE": True,
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


# === Разрешённые источники для CORS ===

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

# Разрешить передачу cookie в CORS
CORS_ALLOW_CREDENTIALS = True


# === Настройки электронной почты ===

DOMAIN = "127.0.0.1:8080"
SITE_NAME = "http://localhost:8080"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# === Конфигурация шаблонов ===

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


# === База данных ===

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# === Валидаторы паролей ===

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


# === Пользовательская модель пользователя ===

AUTH_USER_MODEL = "kluchik.User"


# === Интернационализация ===

LANGUAGE_CODE = "ru"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# === Статические файлы ===

STATIC_URL = "static/"


# === Настройки по умолчанию для первичных ключей ===

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# === Время жизни ссылки для восстановления пароля ===

PASSWORD_RESET_TIMEOUT = 60 * 30  # 30 минут
