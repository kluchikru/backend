from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from rest_framework.serializers import (
    ModelSerializer,
    EmailField,
    CharField,
    ValidationError,
    Serializer,
)
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


# Сериализатор для модели объявлений
class AdvertisementSerializer(ModelSerializer):
    class Meta:
        model = Advertisement
        fields = [
            "id",
            "title",
            "description",
            "created_at",
            "is_active",
            "owner",
            "property_type",
        ]


# Сериализатор для типа недвижимости
class TypesOfAdvertisementSerializer(ModelSerializer):
    class Meta:
        model = PropertyType
        fields = ["id", "name", "description"]


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
