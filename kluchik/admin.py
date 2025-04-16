from django.contrib import admin
from django.utils.html import format_html
from .models import (
    User,
    PropertyType,
    Location,
    Category,
    Advertisement,
    Photo,
    Review,
    FavoriteAdvertisement,
    Notification,
    Statistics,
    Agency,
    Agent,
)


# Настройка для модели User
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "surname",
        "email",
        "is_active",
        "is_staff",
        "is_agent",
        "date_joined",
    )
    list_filter = ("is_active", "is_staff", "is_agent")
    search_fields = ("name", "surname", "email")
    list_display_links = ("name", "surname")
    readonly_fields = ("date_joined",)
    date_hierarchy = "date_joined"


# Настройка для модели Agency
@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "get_agent_count", "get_advertisement_count")
    search_fields = ("name",)
    ordering = ("created_at",)
    readonly_fields = ("get_agent_count", "get_advertisement_count")

    @admin.display(description="Количество агентов")
    def get_agent_count(self, obj):
        return obj.agent_count

    @admin.display(description="Количество объявлений")
    def get_advertisement_count(self, obj):
        return obj.advertisement_count


# Настройка для модели Agent
@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ("user", "agency")
    search_fields = ("user__email", "user__name", "user__surname")
    list_filter = ("agency",)
    ordering = ("agency",)
    raw_id_fields = ("user", "agency")


# Настройка для модели PropertyType
@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


# Настройка для модели Location
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("city", "district", "street", "house")
    list_filter = ("city", "district")
    search_fields = ("city", "district", "street", "house")


# Настройка для модели Category
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


# Настройка для модели Advertisement
@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ("title", "display_price", "status", "date_posted")
    list_filter = ("status", "property_type", "category")
    search_fields = ("title", "description")
    list_display_links = ("title",)
    date_hierarchy = "date_posted"
    raw_id_fields = ("user",)

    @admin.display(description="Цена", ordering="price")
    def display_price(self, obj):
        return obj.formatted_price()


# Настройка для модели Photo
@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ("advertisement", "image_url", "display_order")
    list_filter = ("advertisement",)
    search_fields = ("advertisement__title",)


# Настройка для модели Review
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("advertisement", "user", "display_rating_stars", "short_comment")
    list_filter = ("rating",)
    search_fields = ("advertisement__title", "user__name", "user__surname")
    raw_id_fields = ("user", "advertisement")

    @admin.display(description="Оценка")
    def display_rating_stars(self, obj):
        # Показываем звёздочки вместо чисел
        full_star = "★"
        empty_star = "☆"
        return format_html(
            f'<span style="color: #f39c12;">{full_star * obj.rating}{empty_star * (5 - obj.rating)}</span>'
        )

    @admin.display(description="Комментарий")
    def short_comment(self, obj):
        return (obj.comment[:50] + "...") if len(obj.comment) > 50 else obj.comment


# Настройка для модели FavoriteAdvertisement
@admin.register(FavoriteAdvertisement)
class FavoriteAdvertisementAdmin(admin.ModelAdmin):
    list_display = ("user", "advertisement", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__name", "advertisement__title")
    raw_id_fields = ("user", "advertisement")


# Настройка для модели Notification
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "notification_type", "created_at", "status")
    list_filter = ("notification_type", "status")
    search_fields = ("user__name", "message")
    raw_id_fields = ("user",)


# Настройка для модели Statistics
@admin.register(Statistics)
class StatisticsAdmin(admin.ModelAdmin):
    list_display = ("date", "user_count", "advertisement_count")
    list_filter = ("date",)
    date_hierarchy = "date"
