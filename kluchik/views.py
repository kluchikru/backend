from django.utils import timezone
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta

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


# Представление категорий недвижимости
class PropertyTypeViewSet(ModelViewSet):
    serializer_class = TypesOfAdvertisementSerializer

    def get_queryset(self):
        return PropertyType.objects.all().values_list('name', flat=True)


# Представление, расширяющее JWT-токен с дополнительными полями
class CustomTokenObtainPairViewSet(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# Представление для объявлений за последние 30 дней, исключая проданные и арендованные
class AdvertisementViewSet(ModelViewSet):
    serializer_class = AdvertisementSerializer

    def get_queryset(self):
        thirty_days_ago = timezone.now() - timedelta(days=30)
        return (
            Advertisement.objects.filter(created_at__gte=thirty_days_ago)
            .exclude(
                status__in=["sold", "rented"]  # Исключаем объявления с этими статусами
            )
            .select_related("user", "location", "category", "property_type")
            .values('title', 'price')
        )


# Представление только для активных объявлений
class AdvertisementViewSetActive(ModelViewSet):
    serializer_class = AdvertisementSerializer
    queryset = (
        Advertisement.objects.filter(status="active")
        .select_related("user", "category", "location")
        .prefetch_related("photos")
    )  # список связанных фото


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


# Метод удаления объявления по ID
class DeleteAdvertisement(APIView):
    def delete(self, request, *args, **kwargs):
        # Удалить объявление по ID
        advertisement_id = kwargs.get("pk")
        try:
            advertisement = Advertisement.objects.get(pk=advertisement_id)
            advertisement.delete()
            return Response({"detail": "Объявление удалено."}, status=status.HTTP_204_NO_CONTENT)
        except Advertisement.DoesNotExist:
            return Response({"detail": "Объявление не найдено."}, status=status.HTTP_404_NOT_FOUND)


# Метод обновления статуса объявления
class UpdateAdvertisementStatus(APIView):
    def put(self, request, *args, **kwargs):
        # Получаем ID объявления из URL
        advertisement_id = kwargs.get("pk")
        
        # Получаем новый статус из данных запроса
        new_status = request.data.get("status")

        # Проверяем, что статус передан и является допустимым
        if new_status not in dict(Advertisement.STATUS_CHOICES):
            return Response(
                {"detail": "Неверный статус. Допустимые статусы: draft, active, sold, rented."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Получаем объект объявления по ID
            advertisement = Advertisement.objects.get(pk=advertisement_id)
            
            # Обновляем статус объявления
            advertisement.status = new_status
            advertisement.save()

            return Response({"detail": f"Объявление обновлено на статус '{new_status}'."}, status=status.HTTP_200_OK)
        except Advertisement.DoesNotExist:
            # Если объявление не найдено
            return Response({"detail": "Объявление не найдено."}, status=status.HTTP_404_NOT_FOUND)
