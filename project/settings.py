from pathlib import Path
from datetime import timedelta
from decouple import config
import sentry_sdk
import os

# === Базовые настройки проекта ===

# Корневая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Внимание: храните секретный ключ в .env файле на продакшене!
SECRET_KEY = config("SECRET_KEY")

# Для загрузки медиафайлов
MEDIA_URL = "/media/"  # URL для доступа к медиафайлам
MEDIA_ROOT = os.path.join(BASE_DIR, "media")  # Папка, где будут храниться медиафайлы

# Включайте DEBUG только при локальной разработке
DEBUG = True

ALLOWED_HOSTS = ["*"]


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
    "silk", # анализ запросов
    "django_celery_beat", # рассылка
    "social_django", # oauth2
    # Собственные приложения
    "kluchik",
]


# === Middleware ===

MIDDLEWARE = [
    "silk.middleware.SilkyMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
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
    config("FRONTEND_URL")
]

# Разрешить передачу cookie в CORS
CORS_ALLOW_CREDENTIALS = True


# === Настройки электронной почты ===

DOMAIN = config("DOMAIN")
SITE_NAME = config("FRONTEND_URL")

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# === Настройки электронной почты MailHog ===

# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = "localhost"
# EMAIL_PORT = 1025
# EMAIL_USE_TLS = False
# EMAIL_USE_SSL = False
# EMAIL_HOST_USER = ""
# EMAIL_HOST_PASSWORD = ""


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

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# === Настройки по умолчанию для первичных ключей ===

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# === Время жизни ссылки для восстановления пароля ===

PASSWORD_RESET_TIMEOUT = 60 * 30  # 30 минут

# === Мониторинг ошибок в приложении Sentry ===

sentry_sdk.init(
    dsn="https://183af13013b8d5bf76f0195c4ed3bd48@o4509509062098944.ingest.de.sentry.io/4509509063868496",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)

# === Мониторинг запросов в Silk ===
SILKY_PYTHON_PROFILER = True
SILKY_PYTHON_PROFILER_BINARY = True

# === Планировщик задач Celery ===
CELERY_BROKER_URL = config("REDIS_URL")  # или другой URL Redis
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"

# === OAUTH2 ===

AUTHENTICATION_BACKENDS = (
    "social_core.backends.yandex.YandexOAuth2",  # Добавляем Yandex
    "django.contrib.auth.backends.ModelBackend",  # Стандартный backend
)
SOCIAL_AUTH_REDIRECT_IS_HTTPS = False  # Для локальной разработки
SOCIAL_AUTH_JSONFIELD_ENABLED = (
    True  # Используем JSONField вместо ForeignKey для хранения extra_data
)

SOCIAL_AUTH_USER_MODEL = "kluchik.User"

SOCIAL_AUTH_YANDEX_OAUTH2_KEY = config("YANDEX_CLIENT_ID")
SOCIAL_AUTH_YANDEX_OAUTH2_SECRET = config("YANDEX_CLIENT_SECRET")

SOCIAL_AUTH_YANDEX_OAUTH2_SCOPE = [
    "login:email",
    "login:info",
]
SOCIAL_AUTH_YANDEX_OAUTH2_EXTRA_DATA = ["email", "first_name", "last_name"]

SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",  # 1 — ищем по UID
    "kluchik.auth_pipeline.associate_by_email_or_create",  # 2 —  кастомная логика
    "kluchik.auth_pipeline.save_user_profile",  # 3 — сохранение дополнительных данных
    "social_core.pipeline.social_auth.associate_user",  # 4 — создаём связку
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
)

LOGIN_REDIRECT_URL = "/auth/social/jwt/"
LOGOUT_REDIRECT_URL = config("FRONTEND_URL")
