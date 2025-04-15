from django.contrib import admin
from django.urls import path, include, re_path
from kluchik.views import CustomTokenObtainPairViewSet

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("kluchik.urls")),  # API DRF
    re_path(r"^auth/", include("djoser.urls")),  # Авторизация Djoser
    # path(
    #     "auth/jwt/create/",
    #     CookieTokenObtainPairView.as_view(),
    #     name="jwt-create-cookie",
    # ),
    path(
        "auth/jwt/create/",
        CustomTokenObtainPairViewSet.as_view(),
        name="jwt-create",
    ),
    re_path(r"^auth/", include("djoser.urls.jwt")),  # Авторизация Djoser + JWT
]
