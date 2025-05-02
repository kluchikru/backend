from django.db import models
from django.conf import settings
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db.models import Count, Avg, Sum


# Кастомный менеджер для модели User
class UserManager(BaseUserManager):
    # Метод создания обычного пользователя
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    # Метод создания суперпользователя
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


# Кастомная модель пользователя
class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100, verbose_name="Имя")
    surname = models.CharField(max_length=100, verbose_name="Фамилия")
    patronymic = models.CharField(max_length=100, verbose_name="Отчество")
    phone_number = models.CharField(max_length=15, verbose_name="Номер телефона")
    email = models.EmailField(unique=True, verbose_name="Электронная почта")
    date_joined = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата регистрации"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_staff = models.BooleanField(default=False, verbose_name="Сотрудник")
    is_agent = models.BooleanField(default=False, verbose_name="Агент")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.name} {self.surname}"


# Модель агентства недвижимости
class Agency(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    name = models.CharField(max_length=255, verbose_name="Название")

    class Meta:
        verbose_name = "Агентство"
        verbose_name_plural = "Агентства"

    def __str__(self):
        return self.name

    @property
    def agent_count(self):
        """Количество агентов, связанных с агентством"""
        return self.agents.count()

    @property
    def advertisement_count(self):
        """Количество объявлений, созданных агентами этого агентства"""
        return Advertisement.objects.filter(user__agent__agency=self).count()

    @staticmethod
    def agency_advertisement_count():
        """Аннотирует агентства количеством объявлений"""
        return Agency.objects.annotate(ad_count=Count("agents__user__advertisement"))


# Связь между пользователем и агентством
class Agent(models.Model):
    agency = models.ForeignKey(
        Agency,
        on_delete=models.CASCADE,
        related_name="agents",
        verbose_name="Агентство",
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь"
    )

    class Meta:
        verbose_name = "Агент"
        verbose_name_plural = "Агенты"

    def __str__(self):
        return f"{self.user.name} {self.user.surname} - {self.agency.name}"

    @staticmethod
    def agent_avg_ad_price():
        """Средняя цена объявлений у каждого агента"""
        return Agent.objects.annotate(avg_price=Avg("user__advertisement__price"))


# Тип недвижимости (дом, квартира и т.п.)
class PropertyType(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название типа недвижимости")
    description = models.TextField(verbose_name="Описание типа недвижимости")

    class Meta:
        verbose_name = "Тип недвижимости"
        verbose_name_plural = "Типы недвижимости"

    def __str__(self):
        return self.name


# Локация объекта недвижимости
class Location(models.Model):
    city = models.CharField(max_length=100, verbose_name="Город")
    district = models.CharField(max_length=150, verbose_name="Район")
    street = models.CharField(max_length=150, verbose_name="Улица")
    house = models.CharField(max_length=15, verbose_name="Дом")

    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса"

    def __str__(self):
        return f"{self.city}, {self.district}, {self.street}, {self.house}"


# Категория недвижимости (аренда, продажа)
class Category(models.Model):
    name = models.CharField(
        max_length=100, verbose_name="Название категории недвижимости"
    )
    description = models.TextField(verbose_name="Описание категории недвижимости")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


# Объявление о продаже или аренде недвижимости
class Advertisement(models.Model):
    STATUS_CHOICES = [
        ("draft", "Черновик"),
        ("active", "Актуально"),
        ("sold", "Продано"),
        ("rented", "Арендовано"),
    ]

    title = models.CharField(max_length=200, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Цена")
    square = models.DecimalField(max_digits=4, decimal_places=1, verbose_name="Площадь")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    property_type = models.ForeignKey(
        PropertyType, on_delete=models.CASCADE, verbose_name="Тип недвижимости"
    )
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, verbose_name="Локация"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, verbose_name="Категория"
    )
    date_posted = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата размещения"
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="draft", verbose_name="Статус"
    )

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        ordering = ["-date_posted"]

    def __str__(self):
        return f"{self.title} - {self.formatted_price()}"

    def get_absolute_url(self):
        """URL для отображения деталей объявления"""
        return reverse("advertisement-detail", kwargs={"pk": self.pk})

    @staticmethod
    def total_price():
        """Общая сумма всех объявлений"""
        return Advertisement.objects.aggregate(Sum("price"))["price__sum"]

    def formatted_price(self):
        """Форматированное отображение цены"""
        if self.price >= 1_000_000:
            return f"{self.price / 1_000_000:.2f} млн"
        elif self.price >= 1_000:
            return f"{self.price / 1_000:.2f} тыс"
        return f"{self.price:.2f} руб."


# Фото, прикреплённые к объявлениям
class Photo(models.Model):
    advertisement = models.ForeignKey(
        Advertisement,
        on_delete=models.CASCADE,
        related_name="photos",
        verbose_name="Объявление",
    )
    image_url = models.URLField(verbose_name="URL изображения")
    display_order = models.IntegerField(verbose_name="Порядок отображения")

    class Meta:
        verbose_name = "Фотография"
        verbose_name_plural = "Фотографии"

    def __str__(self):
        return f"Фото для объявления: {self.advertisement.title} - Порядок: {self.display_order}"


# Отзывы пользователей на объявления
class Review(models.Model):
    RATING_CHOICES = [
        (0, "0 — Ужасно"),
        (1, "1 — Очень плохо"),
        (2, "2 — Плохо"),
        (3, "3 — Нормально"),
        (4, "4 — Хорошо"),
        (5, "5 — Отлично"),
    ]

    advertisement = models.ForeignKey(
        Advertisement, on_delete=models.CASCADE, verbose_name="Объявление"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        default=5,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name="Оценка",
    )
    comment = models.TextField(verbose_name="Комментарий")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return f"Отзыв для {self.advertisement.title} от {self.user.name} - Рейтинг: {self.rating}"

    def clean(self):
        """Ограничивает отзывы только объявлениями с категорией 'Аренда'"""
        if self.advertisement.category.name.lower() != "аренда":
            raise ValidationError(
                "Оставлять отзывы можно только для объявлений категории 'Аренда'."
            )


# Модель для хранения избранных объявлений пользователя
class FavoriteAdvertisement(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    advertisement = models.ForeignKey(
        Advertisement, on_delete=models.CASCADE, verbose_name="Объявление"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"

    def __str__(self):
        return f"Избранное: {self.user.name} - {self.advertisement.title}"


# Уведомления, отправляемые пользователю
class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ("new_ad", "Новое объявление"),
        ("ad_update", "Объявление обновлено"),
        ("ad_sold", "Недвижимость продана"),
        ("ad_rented", "Недвижимость арендована"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    advertisement = models.ForeignKey(
        Advertisement, on_delete=models.CASCADE, verbose_name="Объявление"
    )
    notification_type = models.CharField(max_length=50, verbose_name="Тип уведомления")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    status = models.CharField(max_length=50, verbose_name="Статус")
    message = models.TextField(verbose_name="Сообщение")

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"

    def __str__(self):
        return f"Уведомление для {self.user.name}: {self.notification_type}"


# Модель статистики пользователей и объявлений
class Statistics(models.Model):
    date = models.DateField(verbose_name="Дата")
    user_count = models.IntegerField(verbose_name="Пользователи")
    advertisement_count = models.IntegerField(verbose_name="Объявления")

    class Meta:
        verbose_name = "Статистика"
        verbose_name_plural = "Статистика"

    def __str__(self):
        return f"Статистика на {self.date}: Пользователи - {self.user_count}, Объявления - {self.advertisement_count}"
