from django.urls import reverse
from rest_framework.test import APITestCase
from .models import (
    Advertisement,
    PropertyType,
    Category,
    Location,
    User,
    Notification,
    Photo,
)
from django.contrib.auth import get_user_model
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
import tempfile
from PIL import Image

User = get_user_model()


# Тестирование списка объявлений и фильтра
class AdvertisementListViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="test@example.com", name="Test")
        self.property_type = PropertyType.objects.create(name="Квартира")
        self.category = Category.objects.create(name="Продажа")
        self.location = Location.objects.create(
            city="Москва", district="ЦАО", street="Тверская", house="1"
        )
        self.ad = Advertisement.objects.create(
            title="Тест объявление",
            description="Описание",
            price=1000000,
            square=50,
            user=self.user,
            property_type=self.property_type,
            location=self.location,
            category=self.category,
            status="active",
        )

    def test_list_advertisements(self):
        url = reverse("advertisements-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Тест объявление")

    def test_filter_advertisements_by_price(self):
        Advertisement.objects.create(
            title="Дорогое",
            price=5000000,
            square=100,
            user=self.user,
            property_type=self.property_type,
            location=self.location,
            category=self.category,
            status="active",
        )
        url = reverse("advertisements-list") + "?price_min=2000000"
        response = self.client.get(url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["price"], "5000000.00")


# Тестирование регистрации пользователя
class UserRegistrationTests(APITestCase):
    def test_user_registration(self):
        """
        Тестирование регистрации нового пользователя
        """
        url = reverse("user-list")
        data = {
            "email": "test@example.com",
            "name": "Test",
            "surname": "User",
            "password": "strongpassword123",
            "re_password": "strongpassword123",
            "phone_number": "+79991234567",
            "patronymic": "Testovich",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, "test@example.com")


# Тестирование JWT
class JWTAuthenticationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="strongpassword123",
            name="Test",
            surname="User",
            phone_number="+79991234567",
            patronymic="Testovich",
        )

    def test_jwt_token_obtain(self):
        """
        Тестирование получения JWT токена
        """
        url = reverse("jwt-create")
        data = {"email": "test@example.com", "password": "strongpassword123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)


# Тестирование создания объяления
class AdvertisementTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="strongpassword123",
            name="Test",
            surname="User",
            phone_number="+79991234567",
            patronymic="Testovich",
        )
        self.property_type = PropertyType.objects.create(
            name="Квартира", description="Описание"
        )
        self.category = Category.objects.create(name="Продажа", description="Описание")
        self.location = Location.objects.create(
            city="Москва", district="Центральный", street="Тверская", house="1"
        )
        self.advertisement = Advertisement.objects.create(
            title="Тестовое объявление",
            description="Описание",
            price=1000000,
            square=50,
            user=self.user,
            property_type=self.property_type,
            location=self.location,
            category=self.category,
            status="active",
        )
        self.client.force_authenticate(user=self.user)

    def test_create_advertisement(self):
        """
        Тестирование создания объявления
        """
        url = reverse("advertisement-create-list")
        data = {
            "title": "Новое объявление",
            "description": "Описание нового объявления",
            "price": 2000000,
            "square": 60,
            "property_type": self.property_type.id,
            "location": {
                "city": "Москва",
                "district": "Центральный",
                "street": "Тверская",
                "house": "2",
            },
            "category": self.category.id,
            "status": "active",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Advertisement.objects.count(), 2)


# Тестирование избранного у пользователя
class FavoriteAdvertisementTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="strongpassword123",
            name="Test",
            surname="User",
            phone_number="+79991234567",
            patronymic="Testovich",
        )
        self.property_type = PropertyType.objects.create(
            name="Квартира", description="Описание"
        )
        self.category = Category.objects.create(name="Продажа", description="Описание")
        self.location = Location.objects.create(
            city="Москва", district="Центральный", street="Тверская", house="1"
        )
        self.advertisement = Advertisement.objects.create(
            title="Тестовое объявление",
            description="Описание",
            price=1000000,
            square=50,
            user=self.user,
            property_type=self.property_type,
            location=self.location,
            category=self.category,
            status="active",
        )
        self.client.force_authenticate(user=self.user)

    def test_add_to_favorites(self):
        """
        Тестирование добавления объявления в избранное
        """
        url = reverse("advertisements-favorite-add")
        data = {"advertisement_id": self.advertisement.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.advertisement.favoriteadvertisement_set.count(), 1)


# Тестирование отзывов у объявления
class ReviewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="strongpassword123",
            name="Test",
            surname="User",
            phone_number="+79991234567",
            patronymic="Testovich",
        )
        self.property_type = PropertyType.objects.create(
            name="Квартира", description="Описание"
        )
        self.category = Category.objects.create(
            name="Аренда", description="Описание"
        )  # Отзывы только для аренды
        self.location = Location.objects.create(
            city="Москва", district="Центральный", street="Тверская", house="1"
        )
        self.advertisement = Advertisement.objects.create(
            title="Тестовое объявление",
            description="Описание",
            price=1000000,
            square=50,
            user=self.user,
            property_type=self.property_type,
            location=self.location,
            category=self.category,
            status="active",
        )
        self.client.force_authenticate(user=self.user)

    def test_create_review(self):
        """
        Тестирование создания отзыва
        """
        url = reverse("reviews-list")
        data = {
            "advertisement": self.advertisement.id,
            "rating": 5,
            "comment": "Отличное объявление!",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.advertisement.review_set.count(), 1)


# Тестирование уведомлений
class NotificationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="strongpassword123",
            name="Test",
            surname="User",
            phone_number="+79991234567",
            patronymic="Testovich",
        )
        self.client.force_authenticate(user=self.user)

        self.property_type = PropertyType.objects.create(name="Квартира")
        self.category = Category.objects.create(name="Продажа")
        self.location = Location.objects.create(
            city="Москва", district="ЦАО", street="Тверская", house="1"
        )
        self.ad = Advertisement.objects.create(
            title="Тест объявление",
            description="Описание",
            price=1000000,
            square=50,
            user=self.user,
            property_type=self.property_type,
            location=self.location,
            category=self.category,
            status="active",
        )

        self.notification = Notification.objects.create(
            user=self.user,
            advertisement=self.ad,
            notification_type="new_ad",
            status="sent",
            message="Новое объявление в вашем районе",
        )

    def test_user_notifications_list(self):
        """
        Тестирование получения списка уведомлений пользователя
        """
        url = reverse("notifications-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["message"], "Новое объявление в вашем районе")

    def test_notification_status_update(self):
        """
        Тестирование обновления статуса уведомления
        """
        url = reverse("notification-status-update", kwargs={"pk": self.notification.pk})
        data = {"status": "read"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notification.refresh_from_db()
        self.assertEqual(self.notification.status, "read")


class PhotoModelTests(APITestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            name="Test",
            surname="User",
        )

        # Create required related models
        self.property_type = PropertyType.objects.create(name="Apartment")
        self.category = Category.objects.create(name="Sale")
        self.location = Location.objects.create(
            city="Moscow", district="Central", street="Tverskaya", house="1"
        )

        # Create test advertisement
        self.advertisement = Advertisement.objects.create(
            title="Test Ad",
            description="Test description",
            price=1000000,
            square=50,
            user=self.user,
            property_type=self.property_type,
            location=self.location,
            category=self.category,
        )

        # Create a simple test image
        image = Image.new("RGB", (100, 100))
        tmp_file = tempfile.NamedTemporaryFile(suffix=".jpg")
        image.save(tmp_file)
        tmp_file.seek(0)

        self.image_file = SimpleUploadedFile(
            name="test_image.jpg", content=tmp_file.read(), content_type="image/jpeg"
        )

    def test_photo_creation(self):
        """Test creating a photo linked to an advertisement"""
        photo = Photo.objects.create(
            advertisement=self.advertisement, image=self.image_file, display_order=1
        )

        self.assertEqual(Photo.objects.count(), 1)
        self.assertEqual(photo.advertisement, self.advertisement)
        self.assertTrue(photo.image.name.startswith("photos/"))
        self.assertEqual(photo.display_order, 1)

    def test_photo_str_representation(self):
        """Test the string representation of Photo model"""
        photo = Photo.objects.create(
            advertisement=self.advertisement, image=self.image_file, display_order=1
        )

        expected_str = f"Фото для объявления: {self.advertisement.title} - Порядок: 1"
        self.assertEqual(str(photo), expected_str)
