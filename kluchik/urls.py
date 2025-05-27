from rest_framework import routers

from .views import *


# Регистрация ViewSet'ов в роутере
router = routers.DefaultRouter()
router.register("advertisements", AdvertisementListViewSet, basename="advertisements")
router.register(
    "advertisements-latest",
    LatestAdvertisementsViewSet,
    basename="advertisements-latest",
)
router.register(
    "advertisements-popular",
    PopularAdvertisementViewSet,
    basename="advertisements-popular",
)
router.register("agency-popular", PopularAgenciesViewSet, basename="agency-popular")
router.register("types-of-advertisement", TypesOfAdvertisementViewSet)

# Получение маршрутов
urlpatterns = router.urls
