from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from kluchik.views import (
    CustomTokenObtainPairViewSet,
    SetPhoneNumberView,
    AdvertisementDetailViewSet,
    AgencyDetailViewSet,
    NotificationStatusUpdateView,
)

# Тестовая ошибка
def trigger_error(request):
    division_by_zero = 1 / 0


# === Основные URL-маршруты проекта ===

urlpatterns = [
    path('silk/', include('silk.urls', namespace='silk')),  # Django Silk для профилирования
    path("sentry-debug/", trigger_error), # Мониторинг ошибок
    path("admin/", admin.site.urls),  # Панель администратора Django
    path(
        "api/advertisements/<slug:slug>/",
        AdvertisementDetailViewSet.as_view({"get": "retrieve"}),
        name="advertisement-detail",
    ),
    path(
        "api/agencies/<slug:slug>/",
        AgencyDetailViewSet.as_view({"get": "retrieve"}),
        name="agency-detail",
    ),
    path(
        "api/notifications/<int:pk>/status",
        NotificationStatusUpdateView.as_view({"get": "retrieve"}),
        name="notification-status-update",
    ),
    path("api/", include("kluchik.urls")),  # Основное API (приложение kluchik)
    # Обновление номера телефона (требуется авторизация)
    path(
        "auth/users/set_phone_number/",
        SetPhoneNumberView.as_view(),
        name="set_phone_number",
    ),
    # Стандартные маршруты Djoser (регистрация, сброс пароля и т.д.)
    re_path(r"^auth/", include("djoser.urls")),
    # JWT авторизация через кастомный сериализатор
    path(
        "auth/jwt/create/",
        CustomTokenObtainPairViewSet.as_view(),
        name="jwt-create",
    ),
    # JWT endpoints от Djoser (refresh, verify и т.д.)
    re_path(r"^auth/", include("djoser.urls.jwt")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# http://localhost:8000/media/photos/my_image.jpg.
