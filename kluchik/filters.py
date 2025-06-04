from django_filters import rest_framework as filters
from .models import Advertisement

class AdvertisementFilter(filters.FilterSet):
    property_type = filters.NumberFilter(field_name='property_type_id')

    class Meta:
        model = Advertisement
        fields = ['property_type']
