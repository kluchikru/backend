import django_filters
from django_filters.rest_framework import FilterSet
from .models import Advertisement, PropertyType, Category


# Кастомный фильтр для объявлений
class AdvertisementFilter(FilterSet):
    property_type = django_filters.ModelChoiceFilter(
        queryset=PropertyType.objects.all(),
        field_name="property_type",
        label="Тип недвижимости",
        empty_label="Любой тип",
    )
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        field_name="category",
        label="Категория",
        empty_label="Любая категория",
    )
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    square_min = django_filters.NumberFilter(field_name="square", lookup_expr="gte")
    square_max = django_filters.NumberFilter(field_name="square", lookup_expr="lte")

    class Meta:
        model = Advertisement
        fields = [
            "property_type",
            "price_min",
            "price_max",
            "square_min",
            "square_max",
            "category",
        ]
