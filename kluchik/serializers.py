from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from rest_framework.serializers import (
    ModelSerializer,
    EmailField,
    CharField,
    ValidationError,
    Serializer,
)
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from djoser.serializers import (
    UserCreateSerializer as BaseUserCreateSerializer,
    UserSerializer as BaseUserSerializer,
)
from .models import *
import re


# Получение кастомной модели пользователя
User = get_user_model()


# Сериализатор для создания пользователя (расширяет Djoser)
class UserCreateSerializer(BaseUserCreateSerializer):
    email = EmailField(required=True)
    password = CharField(write_only=True)

    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = (
            "id",
            "name",
            "surname",
            "patronymic",
            "phone_number",
            "email",
            "password",
        )

    def validate_email(self, value):
        """Валидация уникальности email"""
        if User.objects.filter(email=value).exists():
            raise ValidationError("Пользователь с таким email уже существует.")
        return value


# Сериализатор для отображения информации о пользователе
class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = (
            "id",
            "name",
            "surname",
            "patronymic",
            "phone_number",
            "email",
        )


# Сериализатор для модели объявлений в ленте
class AdvertisementListSerializer(serializers.ModelSerializer):
    location = serializers.StringRelatedField(read_only=True)
    category = serializers.StringRelatedField(read_only=True)
    property_type = serializers.StringRelatedField(read_only=True)
    image = serializers.SerializerMethodField()  # Поле для первой фотки

    class Meta:
        model = Advertisement
        fields = [
            "id",
            "title",
            "price",
            "square",
            "location",
            "category",
            "property_type",
            "external_url",
            "image",
        ]

    def get_image(self, obj):
        first_photo = obj.photos.order_by("display_order").first()
        if first_photo and first_photo.image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(first_photo.image.url)
            return first_photo.image.url
        return None


# Сериализатор для модели объявлений в профиле пользователя
class MyAdvertisementListSerializer(serializers.ModelSerializer):
    location = serializers.StringRelatedField(read_only=True)
    category = serializers.StringRelatedField(read_only=True)
    property_type = serializers.StringRelatedField(read_only=True)
    image = serializers.SerializerMethodField()  # Поле для первой фотки

    class Meta:
        model = Advertisement
        fields = [
            "id",
            "title",
            "price",
            "square",
            "location",
            "category",
            "property_type",
            "external_url",
            "status",
            "image",
        ]

    def get_image(self, obj):
        first_photo = obj.photos.order_by("display_order").first()
        if first_photo and first_photo.image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(first_photo.image.url)
            return first_photo.image.url
        return None


# Сериализатор для последнего объявления (используется в главной странице - виджет)
class LatestAdvertisementSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Advertisement
        fields = ["id", "title", "price", "image", "category", "external_url"]

    def get_image(self, obj):
        first_photo = obj.photos.order_by("display_order").first()
        if first_photo and first_photo.image:
            request = self.context.get("request")
            return (
                request.build_absolute_uri(first_photo.image.url)
                if request
                else first_photo.image.url
            )
        return None


#  Сериализатор для модели популярных агентств (используется в главной странице - виджет)
class PopularAgencySerializer(serializers.ModelSerializer):
    subscriber_count = serializers.IntegerField()
    active_ads_count = serializers.SerializerMethodField()
    annotated_agent_count = serializers.IntegerField()

    class Meta:
        model = Agency
        fields = [
            "id",
            "name",
            "external_url",
            "subscriber_count",
            "active_ads_count",
            "annotated_agent_count",
        ]

    def get_active_ads_count(self, obj):
        return obj.advertisements.filter(status="active").count()


# Сериализатор для отображения популяного объявления (используется в главной странице - виджет)
class PopularAdvertisementSerializer(serializers.ModelSerializer):
    favorite_count = serializers.IntegerField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Advertisement
        fields = [
            "id",
            "title",
            "price",
            "favorite_count",
            "category",
            "image",
            "external_url",
        ]

    def get_image(self, obj):
        first_photo = obj.photos.order_by("display_order").first()
        if first_photo and first_photo.image:
            request = self.context.get("request")
            return (
                request.build_absolute_uri(first_photo.image.url)
                if request
                else first_photo.image.url
            )
        return None


# Сериализатор для детального просмотра объявления
class AdvertisementDetailSerializer(serializers.ModelSerializer):
    location = serializers.StringRelatedField(read_only=True)
    category = serializers.StringRelatedField(read_only=True)
    property_type = serializers.StringRelatedField(read_only=True)
    agency = serializers.StringRelatedField(read_only=True)
    agency_url = serializers.SerializerMethodField()
    photos = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    surname = serializers.SerializerMethodField()
    patronymic = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Advertisement
        fields = [
            "id",
            "title",
            "description",
            "price",
            "square",
            "location",
            "category",
            "property_type",
            "agency",
            "agency_url",
            "status",
            "date_posted",
            "external_url",
            "photos",
            "phone_number",
            "name",
            "surname",
            "patronymic",
            "email",
            "is_favorite",
        ]

    def get_photos(self, obj):
        photos = obj.photos.order_by("display_order")
        request = self.context.get("request")
        return [
            request.build_absolute_uri(photo.image.url) if request else photo.image.url
            for photo in photos
            if photo.image
        ]

    def get_phone_number(self, obj):
        return obj.user.phone_number if obj.user else None

    def get_name(self, obj):
        return obj.user.name if obj.user else None

    def get_surname(self, obj):
        return obj.user.surname if obj.user else None

    def get_patronymic(self, obj):
        return obj.user.patronymic if obj.user else None

    def get_email(self, obj):
        return obj.user.email if obj.user else None

    def get_agency_url(self, obj):
        return obj.agency.external_url if obj.agency else None

    def get_is_favorite(self, ad):
        request = self.context.get("request")
        user = request.user if request else None
        if user and user.is_authenticated:
            return FavoriteAdvertisement.objects.filter(
                user=user, advertisement=ad
            ).exists()
        return None


# Сериализатор краткой информации об агенте
class AgentShortSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source="user.email")
    phone_number = serializers.CharField(source="user.phone_number")

    class Meta:
        model = Agent
        fields = ["full_name", "email", "phone_number"]

    def get_full_name(self, obj):
        return f"{obj.user.surname} {obj.user.name} {obj.user.patronymic}"


# Сериализатор для детального просмотра агентства
class AgencyDetailSerializer(serializers.ModelSerializer):
    subscriber_count = serializers.IntegerField()
    active_ads_count = serializers.SerializerMethodField()
    annotated_agent_count = serializers.IntegerField()
    agents = AgentShortSerializer(many=True, read_only=True)
    advertisements = AdvertisementListSerializer(many=True, read_only=True)
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Agency
        fields = [
            "id",
            "name",
            "description",
            "created_at",
            "external_url",
            "subscriber_count",
            "active_ads_count",
            "annotated_agent_count",
            "agents",
            "advertisements",
            "is_favorite",
        ]

    def get_active_ads_count(self, obj):
        return obj.advertisements.filter(status="active").count()

    def get_is_favorite(self, agency):
        request = self.context.get("request")
        user = request.user if request else None
        if user and user.is_authenticated:
            return AgencySubscription.objects.filter(user=user, agency=agency).exists()
        return None


# Сериализатор для уведомлений
class NotificationSerializer(serializers.ModelSerializer):
    advertisement_title = serializers.CharField(
        source="advertisement.title", read_only=True
    )
    advertisement_url = serializers.CharField(
        source="advertisement.external_url", read_only=True
    )
    notification_type_display = serializers.CharField(
        source="get_notification_type_display", read_only=True
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "notification_type",
            "notification_type_display",
            "status",
            "status_display",
            "created_at",
            "message",
            "advertisement_title",
            "advertisement_url",
        ]


# Сериализатор для отзывов у объявления
class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_id = serializers.IntegerField(source="user.id", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "advertisement",
            "user",
            "rating",
            "comment",
            "created_at",
            "user_id",
        ]


# Сериализатор для модели объявлений
class AdvertisementSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    property_type = serializers.StringRelatedField(read_only=True)
    location = serializers.StringRelatedField(read_only=True)
    category = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Advertisement
        fields = [
            "id",
            "title",
            "description",
            "price",
            "square",
            "user",
            "property_type",
            "location",
            "category",
            "date_posted",
            "status",
            "advertisement_file",
            "external_url",
            "slug",
        ]


# Сериализатор для списка агентств (используется в ленте)
class AgencyListSerializer(serializers.ModelSerializer):
    subscriber_count = serializers.IntegerField()
    active_ads_count = serializers.SerializerMethodField()
    annotated_agent_count = serializers.IntegerField()

    class Meta:
        model = Agency
        fields = [
            "id",
            "name",
            "external_url",
            "subscriber_count",
            "active_ads_count",
            "annotated_agent_count",
        ]

    def get_active_ads_count(self, obj):
        return obj.advertisements.filter(status="active").count()


# Сериализатор для типа недвижимости
class TypesOfAdvertisementSerializer(ModelSerializer):
    class Meta:
        model = PropertyType
        fields = ["id", "name", "description"]


# Сериализатор для категории недвижимости
class CategoriesOfAdvertisementSerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]


# Сериализатор для ввода локации при создании объявления
class LocationInputSerializer(serializers.Serializer):
    city = serializers.CharField(max_length=100)
    district = serializers.CharField(max_length=150)
    street = serializers.CharField(max_length=150)
    house = serializers.CharField(max_length=15)


# Сериализатор для создания объявления
class AdvertisementCreateSerializer(serializers.ModelSerializer):
    location = LocationInputSerializer()

    class Meta:
        model = Advertisement
        fields = [
            "id",
            "title",
            "description",
            "price",
            "square",
            "property_type",
            "category",
            "location",
            "agency",
        ]

    def create(self, validated_data):
        location_data = validated_data.pop("location")
        location_obj, _ = Location.objects.get_or_create(**location_data)
        advertisement = Advertisement.objects.create(
            location=location_obj, user=self.context["request"].user, **validated_data
        )
        return advertisement


# Сериализатор для фотографий объявлений
class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ["id", "advertisement", "image", "display_order"]


# Сериализатор для редактирования объявления
class AdvertisementEditSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)
    photos_upload = serializers.ListField(
        child=serializers.ImageField(), required=False, write_only=True
    )

    class Meta:
        model = Advertisement
        fields = ["title", "description", "price", "status", "photos", "photos_upload"]

    def update(self, instance, validated_data):
        request = self.context["request"]
        deleted_photo_ids = request.data.getlist("deleted_photos")
        photos_order_json = request.data.get("photos_order")
        photos_upload = validated_data.pop("photos_upload", None)

        # Обновляем поля объявления
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Удаление фото
        if deleted_photo_ids:
            instance.photos.filter(id__in=deleted_photo_ids).delete()

        # Изменение порядка фото
        if photos_order_json:
            import json

            try:
                photos_order = json.loads(photos_order_json)
                for item in photos_order:
                    photo = instance.photos.filter(id=item["id"]).first()
                    if photo:
                        photo.display_order = item["display_order"]
                        photo.save()
            except Exception:
                pass

        # Загрузка новых фото
        if photos_upload is not None:
            for idx, photo in enumerate(photos_upload):
                instance.photos.create(image=photo, display_order=idx)

        # 🔔 Создание уведомлений для избранных пользователей
        favorite_users = FavoriteAdvertisement.objects.filter(
            advertisement=instance
        ).values_list("user", flat=True)
        notifications = [
            Notification(
                user_id=user_id,
                advertisement=instance,
                notification_type="ad_update",
                status="sent",
                message=f"Объявление было обновлено.",
            )
            for user_id in favorite_users
        ]
        Notification.objects.bulk_create(notifications)

        return instance


# Кастомный сериализатор для JWT-токена (добавляет поля is_staff и is_agent)
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["is_staff"] = user.is_staff
        token["is_agent"] = user.is_agent
        return token


# Сериализатор для изменения номера телефона пользователя
class SetPhoneNumberSerializer(Serializer):
    phone_number = CharField(max_length=15)
    current_password = CharField(write_only=True)

    def validate_current_password(self, value):
        """Проверка текущего пароля пользователя"""
        user = self.context["request"].user
        if not check_password(value, user.password):
            raise ValidationError("Неверный пароль")
        return value

    def validate_phone_number(self, value):
        """Проверка формата нового номера телефона"""
        pattern = re.compile(r"^\+\d{10,14}$")
        if not pattern.match(value):
            raise ValidationError(
                "Номер должен быть в формате +7XXXXXXXXXX и содержать от 11 до 15 цифр"
            )
        return value

    def save(self, **kwargs):
        """Сохраняет новый номер телефона"""
        user = self.context["request"].user
        user.phone_number = self.validated_data["phone_number"]
        user.save()
        return user
