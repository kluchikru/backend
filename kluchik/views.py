from django.utils import timezone
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.filters import SearchFilter
from django.db.models import Case, When, IntegerField
from django_filters.rest_framework import DjangoFilterBackend
from .filters import AdvertisementFilter
from rest_framework.decorators import action
from rest_framework import status
from datetime import timedelta

from typing import Any, Dict, List
from django.db.models import QuerySet
from .models import *
from .serializers import *


# Представление для управления объектами недвижимости
class AdvertisementListViewSet(ReadOnlyModelViewSet):
    """
    Представление только для чтения списка активных объектов недвижимости.
    Позволяет выполнять фильтрацию и поиск по объявлениям.
    """

    serializer_class = AdvertisementListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = AdvertisementFilter
    search_fields = ["title", "description"]

    def get_queryset(self) -> QuerySet:
        """
        Возвращает queryset активных объявлений с предварительной выборкой
        связанных объектов для оптимизации запросов.
        """
        return (
            Advertisement.objects.filter(status="active")
            .select_related("location", "category", "property_type")
            .prefetch_related("photos")
        )


# Представление для получения последних 3 объявлений
class LatestAdvertisementsViewSet(ReadOnlyModelViewSet):
    """
    Представление для получения последних 3 активных объявлений.
    """

    serializer_class = AdvertisementListSerializer

    def get_queryset(self) -> QuerySet:
        """
        Возвращает последние 3 активных объявления, отсортированных по дате публикации.
        """
        return Advertisement.objects.filter(status="active").order_by("-date_posted")[
            :3
        ]


# Представление для получения 3 самых популярных агентств
class PopularAgenciesViewSet(ReadOnlyModelViewSet):
    """
    Представление для получения 3 самых популярных агентств по количеству подписчиков.
    """

    serializer_class = PopularAgencySerializer

    def get_queryset(self) -> QuerySet:
        """
        Возвращает 3 агентства с наибольшим количеством подписчиков.
        """
        return Agency.with_count().order_by("-subscriber_count")[:3]


# Представление для получения 3 самых популярных объявления
class PopularAdvertisementViewSet(ReadOnlyModelViewSet):
    """
    Представление для получения 3 самых популярных объявлений по количеству добавлений в избранное.
    """

    serializer_class = PopularAdvertisementSerializer

    def get_queryset(self) -> QuerySet:
        """
        Возвращает 3 самых популярных активных объявления,
        отсортированных по количеству добавлений в избранное и дате публикации.
        """
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
    """
    Представление для получения детальной информации об активном объявлении по slug.
    """

    serializer_class = AdvertisementDetailSerializer
    lookup_field = "slug"

    def get_queryset(self) -> QuerySet:
        """
        Возвращает queryset активных объявлений с предварительной выборкой
        связанных объектов для повышения производительности.
        """
        return (
            Advertisement.objects.filter(status="active")
            .select_related("location", "category", "property_type", "user")
            .prefetch_related("photos")
        )

    def get_serializer_context(self) -> Dict[str, Any]:
        """
        Добавляет объект запроса (request) в контекст сериализатора.
        """
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


# Представление для получения избранных объявлений пользователя
class FavoriteAdvertisementsListView(ModelViewSet):
    """
    Представление для управления избранными объявлениями пользователя.
    """

    serializer_class = AdvertisementListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        """
        Возвращает queryset объявлений, добавленных в избранное текущим пользователем.
        """
        user = self.request.user
        # Получаем избранные объявления пользователя через связь FavoriteAdvertisement
        return Advertisement.objects.filter(favoriteadvertisement__user=user).order_by(
            "-favoriteadvertisement__created_at"
        )

    @action(detail=False, methods=["post"])
    def add(self, request: Request) -> Response:
        """
        Добавляет объявление в избранное текущего пользователя.
        """
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
    def remove(self, request: Request) -> Response:
        """
        Удаляет объявление из избранного текущего пользователя.
        """
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
class MyAdvertisementListView(ModelViewSet):
    """
    Представление для получения объявлений текущего пользователя.
    """

    serializer_class = MyAdvertisementListSerializer

    def get_queryset(self) -> QuerySet:
        """
        Возвращает queryset объявлений, принадлежащих текущему пользователю,
        с аннотированным полем для упорядочивания по статусу.
        """
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
    """
    Представление для получения списка активныx (неархивированные) уведомлений текущего пользователя.
    """

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        """
        Возвращает queryset уведомлений пользователя, исключая архивированные.
        """
        # Фильтруем уведомления пользователя, исключая "archived"
        return (
            Notification.objects.filter(user=self.request.user)
            .exclude(status="archived")
            .order_by("-created_at")
        )


# Представление для получения архивированных уведомлений пользователя
class ArchivedNotificationListView(ReadOnlyModelViewSet):
    """
    Представление для получения архивированных уведомлений текущего пользователя.
    """

    serializer_class = NotificationSerializer

    def get_queryset(self) -> QuerySet:
        """
        Возвращает queryset архивированных уведомлений пользователя.
        """
        return Notification.objects.filter(
            user=self.request.user, status="archived"
        ).order_by("-created_at")


# Представление для обновления статуса уведомления
class NotificationStatusUpdateView(ModelViewSet):
    """
    Представление для обновления статуса уведомления.
    """

    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    lookup_field = "pk"

    def get_object(self) -> Notification:
        """
        Получает объект уведомления и проверяет принадлежность текущему пользователю.
        """
        notification = super().get_object()
        # Проверяем, что уведомление принадлежит текущему пользователю
        if notification.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Нет доступа к этому уведомлению")
        return notification

    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Обрабатывает PATCH-запрос для обновления статуса уведомления.
        """
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


# Представление для управления отзывами к объявлениям
class ReviewViewSet(ModelViewSet):
    """
    Представление для управления отзывами к объявлениям.
    """

    serializer_class = ReviewSerializer
    queryset = Review.objects.all()

    def get_queryset(self) -> QuerySet:
        """
        Возвращает queryset отзывов.
        """
        if self.action == "list":
            advertisement_id = self.request.query_params.get("advertisement")
            if advertisement_id:
                return Review.objects.filter(
                    advertisement_id=advertisement_id
                ).order_by("-created_at")
            return Review.objects.none()
        return Review.objects.all()

    def get_permissions(self) -> List[Any]:
        """
        Определяет права доступа в зависимости от действия.
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated()]
        return []  # Разрешить доступ без авторизации (AllowAny)

    def perform_create(self, serializer: Any) -> None:
        """
        При создании отзыва автоматически назначает пользователя.
        """
        serializer.save(user=self.request.user)

    def perform_update(self, serializer: Any) -> None:
        """
        Проверяет права пользователя перед обновлением отзыва.
        """
        review = self.get_object()
        if review.user != self.request.user:
            raise PermissionDenied("Редактировать можно только свои отзывы.")
        serializer.save()

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Проверяет права пользователя перед удалением отзыва.
        """
        review = self.get_object()
        if review.user != request.user:
            raise PermissionDenied("Удалять можно только свои отзывы.")
        return super().destroy(request, *args, **kwargs)


# Представление для получения детальной информации об агентстве
class AgencyDetailViewSet(ReadOnlyModelViewSet):
    """
    Представление для получения детальной информации об агентстве.
    """

    serializer_class = AgencyDetailSerializer
    lookup_field = "slug"

    def get_queryset(self) -> QuerySet:
        """
        Возвращает queryset агентств с аннотациями и предварительной загрузкой связанных объектов.
        """
        return Agency.objects.annotate(
            subscriber_count=Count("subscribers", distinct=True),
            annotated_agent_count=Count("agents", distinct=True),
        ).prefetch_related(
            "agents__user",
            "advertisements__location",
            "advertisements__category",
            "advertisements__property_type",
            "advertisements__photos",
        )

    def get_serializer_context(self) -> Dict[str, Any]:
        """
        Добавляет объект запроса в контекст сериализатора.
        """
        context = super().get_serializer_context()
        context["request"] = self.request  # для абсолютного пути фото
        return context


# Представление для получения списка агентств
class AgencyListViewSet(ReadOnlyModelViewSet):
    """
    Представление для получения списка агентств.
    """

    serializer_class = AgencyListSerializer
    filter_backends = [SearchFilter]
    search_fields = ["name"]

    queryset = Agency.objects.annotate(
        subscriber_count=Count("subscribers", distinct=True),
        annotated_agent_count=Count("agents", distinct=True),
        # active_ads_count мы считаем через метод get_active_ads_count в сериализаторе
    ).order_by("name")


# Представление для получения избранных агентств пользователя
class FavoriteAgenciesListView(ModelViewSet):
    """
    Представление для управления списком избранных агентств пользователя.
    """

    serializer_class = AgencyListSerializer

    def get_queryset(self) -> QuerySet:
        """
        Возвращает queryset избранных агентств текущего пользователя с аннотациями.
        """
        user = self.request.user
        # Получаем избранные агентства пользователя через связь AgencySubscription
        return Agency.objects.filter(subscribers=user).annotate(
            subscriber_count=Count("subscribers", distinct=True),
            annotated_agent_count=Count("agents", distinct=True),
        )

    @action(detail=False, methods=["post"])
    def add(self, request: Any) -> Response:
        """
        Добавляет агентство в список избранных пользователя.
        """
        user = request.user
        agency_id = request.data.get("agency_id")
        if not agency_id:
            return Response(
                {"error": "agency_id required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Создаем подписку (если не существует)
        subscription, created = AgencySubscription.objects.get_or_create(
            user=user, agency_id=agency_id
        )
        if created:
            return Response({"status": "added"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"status": "already exists"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["delete"])
    def remove(self, request: Any) -> Response:
        """
        Удаляет агентство из списка избранных пользователя.
        """
        user = request.user
        agency_id = request.data.get("agency_id")
        if not agency_id:
            return Response(
                {"error": "agency_id required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        deleted, _ = AgencySubscription.objects.filter(
            user=user, agency_id=agency_id
        ).delete()
        if deleted:
            return Response({"status": "removed"}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "not found"}, status=status.HTTP_404_NOT_FOUND)


# Представление для управления типами недвижимости
class TypesOfAdvertisementViewSet(ReadOnlyModelViewSet):
    """
    Представление для управления типами недвижимости.
    """

    queryset = PropertyType.objects.all().order_by("name")
    serializer_class = TypesOfAdvertisementSerializer


# Представление для управления типами недвижимости
class CategoriesOfAdvertisementViewSet(ReadOnlyModelViewSet):
    """
    Представление для управления категориями недвижимости.
    """

    queryset = Category.objects.all().order_by("name")
    serializer_class = CategoriesOfAdvertisementSerializer


# Представление для создания объявлений
class AdvertisementCreateViewSet(ModelViewSet):
    """
    Представление для создания объявлений.
    """

    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        """
        Возвращает queryset объявлений текущего пользователя.
        """
        return Advertisement.objects.filter(user=self.request.user)


# Представление для редактирования объявлений
class AdvertisementEditViewSet(ModelViewSet):
    """
    Представление для редактирования объявлений.
    """

    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementEditSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        """
        Возвращает queryset объявлений текущего пользователя.
        """
        return Advertisement.objects.filter(user=self.request.user)


# Представление для управления фотографиями объявлений
class PhotoViewSet(ModelViewSet):
    """
    Представление для управления фотографиями объявлений.
    """

    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer

    def perform_create(self, serializer: Any) -> None:
        """
        Сохраняет новую фотографию.
        """
        serializer.save()


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
