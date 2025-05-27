from rest_framework import routers

from .views import *


# Регистрация ViewSet'ов в роутере
router = routers.DefaultRouter()
router.register("advertisements", AdvertisementViewSet, basename="advertisement")
router.register("types-of-advertisement", TypesOfAdvertisementViewSet)

# Получение маршрутов
urlpatterns = router.urls
