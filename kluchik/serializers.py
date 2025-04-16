from rest_framework.serializers import (
    ModelSerializer,
    EmailField,
    CharField,
    ValidationError,
)
from django.contrib.auth import get_user_model
from djoser.serializers import (
    UserCreateSerializer as BaseUserCreateSerializer,
    UserSerializer as BaseUserSerializer,
)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import *

User = get_user_model()


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
        if User.objects.filter(email=value).exists():
            raise ValidationError("Пользователь с таким email уже существует.")
        return value


# 🔹
class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = ("id", "name", "surname", "patronymic", "phone_number", "email")


class TypesOfAdvertisementSerializer(ModelSerializer):
    class Meta:
        model = PropertyType
        fields = ["id", "name", "description"]

# Кастомные поля в JWT 
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['user'] = user.__str__()
        token['email'] = user.email
        token['phone_number'] = user.phone_number
        token['is_staff'] = user.is_staff
        token['is_agent'] = user.is_agent
        return token
