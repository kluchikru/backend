from django.contrib import admin
from django.utils.html import format_html
from .models import *


# Админка для модели User
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # Отображаемые поля в списке пользователей
    list_display = (
        "name",
        "surname",
        "email",
        "is_active",
        "is_staff",
        "is_agent",
        "date_joined",
    )
    # Фильтры по статусам
    list_filter = ("is_active", "is_staff", "is_agent")
    # Поиск по имени, фамилии и email
    search_fields = ("name", "surname", "email")
    # Ссылки на редактирование
    list_display_links = ("name", "surname")
    # Только для чтения — нельзя редактировать вручную
    readonly_fields = ("date_joined",)
    # Упрощение навигации по дате
    date_hierarchy = "date_joined"


# Админка для модели Agency
@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    # Отображаем название и статистику по агентству
    list_display = ("name", "created_at", "get_agent_count", "get_advertisement_count")
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
    list_display = ("title", "display_price", "status", "date_posted")
    list_filter = ("status", "property_type", "category")
    search_fields = ("title", "description")
    list_display_links = ("title",)
    date_hierarchy = "date_posted"
    raw_id_fields = ("user",)

    # Показываем цену в более читабельном формате
    @admin.display(description="Цена", ordering="price")
    def display_price(self, obj):
        return obj.formatted_price()


# Админка для модели Photo
@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ("advertisement", "image_url", "display_order")
    list_filter = ("advertisement",)
    search_fields = ("advertisement__title",)


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
    list_display = ("user", "notification_type", "created_at", "status")
    list_filter = ("notification_type", "status")
    search_fields = ("user__name", "message")
    raw_id_fields = ("user",)


# Админка для модели статистики
@admin.register(Statistics)
class StatisticsAdmin(admin.ModelAdmin):
    list_display = ("date", "user_count", "advertisement_count")
    list_filter = ("date",)
    date_hierarchy = "date"
