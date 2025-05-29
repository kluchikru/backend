from django.utils import timezone
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.filters import SearchFilter
from django.db.models import Case, When, IntegerField
from rest_framework.decorators import action
from rest_framework import status
from datetime import timedelta

from .models import *
from .serializers import *


# Представление для управления объектами недвижимости
class AdvertisementListViewSet(ReadOnlyModelViewSet):
    serializer_class = AdvertisementListSerializer
    filter_backends = [SearchFilter]
    search_fields = ["title", "description"]

    def get_queryset(self):
        return (
            Advertisement.objects.filter(status="active")
            .select_related("location", "category", "property_type")
            .prefetch_related("photos")
        )


# Представление для получения последних 3 объявлений
class LatestAdvertisementsViewSet(ReadOnlyModelViewSet):
    serializer_class = AdvertisementListSerializer

    def get_queryset(self):
        return Advertisement.objects.filter(status="active").order_by("-date_posted")[
            :3
        ]


# Представление для получения 3 самых популярных агентств
class PopularAgenciesViewSet(ReadOnlyModelViewSet):
    serializer_class = PopularAgencySerializer

    def get_queryset(self):
        return Agency.with_count().order_by("-subscriber_count")[:3]


# Представление для получения 3 самых популярных объявления
class PopularAdvertisementViewSet(ReadOnlyModelViewSet):
    serializer_class = PopularAdvertisementSerializer

    def get_queryset(self):
        return (
            Advertisement.objects.filter(status="active")  # только активные объявления
            .annotate(
                favorite_count=Count(
                    "favoriteadvertisement"
                )  # считаем количество избранных
            )
            .order_by(
                "-favorite_count",
                "-date_posted",  # сортируем по количеству избранных и дате
            )[:3]
        )


# Представление для получения детальной информации об объявлении
class AdvertisementDetailViewSet(ReadOnlyModelViewSet):
    serializer_class = AdvertisementDetailSerializer
    filter_backends = [SearchFilter]
    search_fields = ["title", "description"]
    lookup_field = "slug"  # <-- Ищем по slug вместо pk

    def get_queryset(self):
        return (
            Advertisement.objects.filter(status="active")
            .select_related("location", "category", "property_type", "user")
            .prefetch_related("photos")
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


# Представление для получения избранных объявлений пользователя
class FavoriteAdvertisementsListView(ModelViewSet):
    serializer_class = AdvertisementListSerializer

    def get_queryset(self):
        user = self.request.user
        # Получаем избранные объявления пользователя через связь FavoriteAdvertisement
        return Advertisement.objects.filter(favoriteadvertisement__user=user).order_by(
            "-favoriteadvertisement__created_at"
        )

    @action(detail=False, methods=["post"])
    def add(self, request):
        user = request.user
        ad_id = request.data.get("advertisement_id")
        if not ad_id:
            return Response(
                {"error": "advertisement_id required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        favorite, created = FavoriteAdvertisement.objects.get_or_create(
            user=user, advertisement_id=ad_id
        )
        if created:
            return Response({"status": "added"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"status": "already exists"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["delete"])
    def remove(self, request):
        user = request.user
        ad_id = request.data.get("advertisement_id")
        if not ad_id:
            return Response(
                {"error": "advertisement_id required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        deleted, _ = FavoriteAdvertisement.objects.filter(
            user=user, advertisement_id=ad_id
        ).delete()
        if deleted:
            return Response({"status": "removed"}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "not found"}, status=status.HTTP_404_NOT_FOUND)


# Представление для получения объявлений пользователя
class MyAdvertisementListView(ReadOnlyModelViewSet):
    serializer_class = MyAdvertisementListSerializer

    def get_queryset(self):
        return (
            Advertisement.objects.filter(user=self.request.user)
            .annotate(
                status_order=Case(
                    When(status="draft", then=0),
                    When(status="active", then=1),
                    When(status="rented", then=2),
                    When(status="sold", then=3),
                    default=4,
                    output_field=IntegerField(),
                )
            )
            .order_by("status_order", "-date_posted")
        )


# Представление для получения уведомлений пользователя
class UserNotificationListView(ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        # Фильтруем уведомления пользователя, исключая "archived"
        return (
            Notification.objects.filter(user=self.request.user)
            .exclude(status="archived")
            .order_by("-created_at")
        )


# Представление для получения архивированных уведомлений пользователя
class ArchivedNotificationListView(ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user, status="archived"
        ).order_by("-created_at")


class NotificationStatusUpdateView(ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    lookup_field = "pk"

    def get_object(self):
        notification = super().get_object()
        # Проверяем, что уведомление принадлежит текущему пользователю
        if notification.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Нет доступа к этому уведомлению")
        return notification

    def patch(self, request, *args, **kwargs):
        notification = self.get_object()
        new_status = request.data.get("status")

        valid_statuses = dict(Notification.STATUS_CHOICES).keys()
        if new_status not in valid_statuses:
            return Response(
                {"error": "Неверный статус"}, status=status.HTTP_400_BAD_REQUEST
            )

        notification.status = new_status
        notification.save()

        serializer = self.get_serializer(notification)
        return Response(serializer.data)


# Представление для управления типами недвижимости
class TypesOfAdvertisementViewSet(ReadOnlyModelViewSet):
    queryset = PropertyType.objects.all()
    serializer_class = TypesOfAdvertisementSerializer


#! DJANGO 1-4
# Представление категорий недвижимости
class PropertyTypeViewSet(ModelViewSet):
    serializer_class = TypesOfAdvertisementSerializer

    def get_queryset(self):
        return PropertyType.objects.all().values_list("name", flat=True)


# Представление, расширяющее JWT-токен с дополнительными полями
class CustomTokenObtainPairViewSet(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# Представление только для активных объявлений
class AdvertisementViewSetActive(ModelViewSet):
    serializer_class = AdvertisementSerializer
    queryset = (
        Advertisement.objects.filter(status="active")
        .select_related("user", "category", "location")
        .prefetch_related("photos")
    )


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
            return Response(
                {"detail": "Объявление удалено."}, status=status.HTTP_204_NO_CONTENT
            )
        except Advertisement.DoesNotExist:
            return Response(
                {"detail": "Объявление не найдено."}, status=status.HTTP_404_NOT_FOUND
            )


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
                {
                    "detail": "Неверный статус. Допустимые статусы: draft, active, sold, rented."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Получаем объект объявления по ID
            advertisement = Advertisement.objects.get(pk=advertisement_id)

            # Обновляем статус объявления
            advertisement.status = new_status
            advertisement.save()

            return Response(
                {"detail": f"Объявление обновлено на статус '{new_status}'."},
                status=status.HTTP_200_OK,
            )
        except Advertisement.DoesNotExist:
            # Если объявление не найдено
            return Response(
                {"detail": "Объявление не найдено."}, status=status.HTTP_404_NOT_FOUND
            )


# Представление для объявлений за последние 30 дней, исключая проданные и арендованные
class AdvertisementViewSetTest(ModelViewSet):
    serializer_class = AdvertisementSerializer

    def get_queryset(self):
        thirty_days_ago = timezone.now() - timedelta(days=30)
        return (
            Advertisement.objects.filter(date_posted__gte=thirty_days_ago)
            .exclude(
                status__in=[
                    "sold",
                    "rented",
                    "draft",
                ]  # Исключаем объявления с этими статусами
            )
            .select_related("user", "location", "category", "property_type")
            .values("title", "price")
        )
