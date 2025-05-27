from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import matplotlib.pyplot as plt
import io
from django.db.models import Q
from .models import *


# Админка для модели User
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # Отображаемые поля в списке пользователей
    list_display = (
        "name",
        "surname",
        "email",
        "phone_number",
        "is_active",
        "is_staff",
        "is_agent",
        "date_joined",
        "get_subscription_count",
    )
    # Фильтры по статусам
    list_filter = ("is_active", "is_staff", "is_agent")
    # Поиск по имени, фамилии и email
    search_fields = ("name", "surname", "email", "phone_number")
    # Ссылки на редактирование
    list_display_links = ("name", "surname")
    # Только для чтения — нельзя редактировать вручную
    readonly_fields = ("date_joined",)
    # Упрощение навигации по дате
    date_hierarchy = "date_joined"

    # Метод для отображения количества подписок пользователя
    @admin.display(description="Количество подписок")
    def get_subscription_count(self, obj):
        return obj.subscriptions.count()  # Считаем количество подписок


# Админка для модели Agency
@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    # Отображаем название и статистику по агентству
    list_display = (
        "name",
        "created_at",
        "get_subscriber_count",
        "get_agent_count",
        "get_advertisement_count",
    )
    search_fields = ("name",)
    ordering = ("created_at",)
    readonly_fields = ("get_agent_count", "get_advertisement_count")

    # Пользовательское отображение количества агентов
    @admin.display(description="Количество агентов")
    def get_agent_count(self, obj):
        return obj.agent_count

    # Пользовательское отображение количества объявлений
    @admin.display(description="Количество объявлений")
    def get_advertisement_count(self, obj):
        return obj.advertisement_count

    # Аннотация подписчиков
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(subscriber_count=Count("subscribers", distinct=True))

    # Пользовательское отображение количества подписчиков
    @admin.display(description="Количество подписчиков", ordering="subscriber_count")
    def get_subscriber_count(self, obj):
        return getattr(obj, "subscriber_count", 0)


# Админка для модели Agent
@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ("user", "agency")
    # Поиск по связанной модели пользователя
    search_fields = ("user__email", "user__name", "user__surname")
    list_filter = ("agency",)
    ordering = ("agency",)
    raw_id_fields = ("user", "agency")


# Админка для модели PropertyType (типы недвижимости)
@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


# Админка для модели Location (локации объектов)
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("city", "district", "street", "house")
    list_filter = ("city", "district")
    search_fields = ("city", "district", "street", "house")


# Админка для модели Category (категории недвижимости)
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


# Админка для модели Advertisement
@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "display_price",
        "status",
        "date_posted",
        "advertisement_file",
        "external_url",
    )
    list_filter = ("status", "category", "property_type")
    search_fields = ("title", "description", "external_url")
    list_display_links = ("title",)
    date_hierarchy = "date_posted"
    raw_id_fields = ("user",)
    readonly_fields = (
        "slug",
        "external_url",
    )  # Устанавливаем эти поля как доступные только для чтения

    # Показываем цену в более читабельном формате
    @admin.display(description="Цена", ordering="price")
    def display_price(self, obj):
        return obj.formatted_price()

    def get_search_results(self, request, queryset, search_term):
        if not search_term:
            return queryset, False
        # Стандартный поиск
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )
        # Расширенный contains-поиск
        contains_qs = self.model.objects.filter(
            Q(title__contains=search_term) | Q(description__contains=search_term)
        )

        final_qs = queryset | contains_qs
        return final_qs.distinct(), use_distinct


# Админка для модели Photo
@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ("advertisement", "get_image_preview", "display_order")
    search_fields = ("advertisement__title",)
    raw_id_fields = ("advertisement",)

    def get_image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" />')
        return "Нет изображения"

    get_image_preview.short_description = "Изображение"


# Админка для модели Review
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("advertisement", "user", "display_rating_stars", "short_comment")
    list_filter = ("rating",)
    search_fields = ("advertisement__title", "user__name", "user__surname")
    raw_id_fields = ("user", "advertisement")

    # Показываем рейтинг в виде звёзд
    @admin.display(description="Оценка")
    def display_rating_stars(self, obj):
        full_star = "★"
        empty_star = "☆"
        return format_html(
            f'<span style="color: #f39c12;">{full_star * obj.rating}{empty_star * (5 - obj.rating)}</span>'
        )

    # Сокращаем длинные комментарии до первых 50 символов
    @admin.display(description="Комментарий")
    def short_comment(self, obj):
        return (obj.comment[:50] + "...") if len(obj.comment) > 50 else obj.comment


# Админка для модели избранных объявлений
@admin.register(FavoriteAdvertisement)
class FavoriteAdvertisementAdmin(admin.ModelAdmin):
    list_display = ("user", "advertisement", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__name", "advertisement__title")
    raw_id_fields = ("user", "advertisement")


# Админка для модели уведомлений
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "advertisement",
        "notification_type",
        "created_at",
        "status",
    )
    list_filter = ("notification_type", "status")
    search_fields = ("user__name", "message")
    raw_id_fields = ("user", "advertisement")


# Админка для модели статистики
@admin.register(Statistics)
class StatisticsAdmin(admin.ModelAdmin):
    list_display = ("date", "user_count", "advertisement_count")
    list_filter = ("date",)
    date_hierarchy = "date"
    actions = ["generate_pdf_with_pie"]

    @admin.action(description="PDF с круговой диаграммой")
    def generate_pdf_with_pie(self, request, queryset):
        # Сбор данных
        total_users = sum(stat.user_count for stat in queryset)
        total_ads = sum(stat.advertisement_count for stat in queryset)

        labels = ["Пользователи", "Объявления"]
        sizes = [total_users, total_ads]
        colors = ["#66b3ff", "#ff9999"]

        # Создание круговой диаграммы
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct="%1.1f%%", colors=colors, startangle=90)
        ax.axis("equal")

        # Сохраняем диаграмму во временный буфер
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format="PNG")
        plt.close(fig)
        img_buffer.seek(0)

        # PDF с вставленной диаграммой
        pdf_buffer = io.BytesIO()
        p = canvas.Canvas(pdf_buffer, pagesize=A4)
        p.setFont("Helvetica-Bold", 16)

        # Вставка изображения
        image = ImageReader(img_buffer)
        p.drawImage(image, 100, 400, width=400, height=400)

        p.showPage()
        p.save()
        pdf_buffer.seek(0)

        return HttpResponse(pdf_buffer, content_type="application/pdf")


# Админка для модели AgencySubscription
@admin.register(AgencySubscription)
class AgencySubscriptionAdmin(admin.ModelAdmin):
    raw_id_fields = ("user", "agency")
    # Отображаемые поля
    list_display = ("user", "agency")
    # Поиск по пользователям и агентствам
    search_fields = ("user__name", "agency__name")
    # Фильтрация по агентствам
    list_filter = ("agency",)
    # Сортировка по дате подписки
    ordering = ("subscribed_at",)
    # Поле только для чтения
    readonly_fields = ("subscribed_at",)
