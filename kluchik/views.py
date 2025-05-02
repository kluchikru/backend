from django.utils import timezone
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from django.conf import settings

from .models import *
from .serializers import *


# Представление для управления пользователями
class UsersViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# Представление для управления типами недвижимости
class TypesOfAdvertisementViewSet(ModelViewSet):
    queryset = PropertyType.objects.all()
    serializer_class = TypesOfAdvertisementSerializer


# Представление, расширяющее JWT-токен с дополнительными полями
class CustomTokenObtainPairViewSet(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# Представление для объявлений за последние 30 дней, исключая проданные и арендованные
class AdvertisementViewSet(ModelViewSet):
    serializer_class = AdvertisementSerializer

    def get_queryset(self):
        thirty_days_ago = timezone.now() - timedelta(days=30)
        return Advertisement.objects.filter(created_at__gte=thirty_days_ago).exclude(
            status__in=["sold", "rented"]  # Исключаем объявления с этими статусами
        )


# Представление только для активных объявлений
class AdvertisementViewSetActive(ModelViewSet):
    queryset = Advertisement.objects.filter(status="active")
    serializer_class = AdvertisementSerializer


# Представление для смены номера телефона пользователя
class SetPhoneNumberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = SetPhoneNumberSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "Номер телефона успешно обновлен"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

