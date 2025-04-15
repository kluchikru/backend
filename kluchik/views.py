from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from django.conf import settings

from .models import *
from .serializers import *


# API для пользователей
class UsersViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# API для типов недвижимости
class TypesOfAdvertisementViewSet(ModelViewSet):
    queryset = PropertyType.objects.all()
    serializer_class = TypesOfAdvertisementSerializer

# Дополнительные поля в JWT
class CustomTokenObtainPairViewSet(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# # Авторизация и запись в Cookie JWT
# class CookieTokenObtainPairView(TokenObtainPairView):
#     def post(self, request, *args, **kwargs):
#         response = super().post(request, *args, **kwargs)
#         if response.status_code == 200:
#             access = response.data["access"]
#             refresh = response.data["refresh"]

#             response.set_cookie(
#                 key=settings.SIMPLE_JWT["AUTH_COOKIE"],
#                 value=access,
#                 httponly=True,
#                 secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
#                 samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
#                 max_age=int(
#                     settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()
#                 ),
#             )
#             response.set_cookie(
#                 key=settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"],
#                 value=refresh,
#                 httponly=True,
#                 secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
#                 samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
#                 max_age=int(
#                     settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()
#                 ),
#             )
#             # Можно удалить токены из JSON, если не хочешь их отдавать
#             response.data.pop("access")
#             response.data.pop("refresh")
#         return response


# # Выход и удаление cookie
# class LogoutView(APIView):
#     def post(self, request):
#         response = Response({"message": "Logged out successfully"}, status=200)
#         response.delete_cookie("access_token")
#         response.delete_cookie("refresh_token")
#         return response
