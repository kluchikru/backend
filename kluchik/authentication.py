from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Берём токен из cookies
        access_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE"])
        if access_token is None:
            return None

        # Притворяемся, что токен пришёл в заголовке
        request.META["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"
        return super().authenticate(request)
