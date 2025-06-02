from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register("advertisements", AdvertisementListViewSet, basename="advertisements")
router.register("agencies", AgencyListViewSet, basename="agencies")
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
router.register(
    "advertisements-favorite",
    FavoriteAdvertisementsListView,
    basename="advertisements-favorite",
)
router.register(
    "agencies-favorite",
    FavoriteAgenciesListView,
    basename="agencies-favorite",
)
router.register(
    "my-advertisements", MyAdvertisementListView, basename="my-advertisements"
)
router.register("agency-popular", PopularAgenciesViewSet, basename="agency-popular")
router.register("notifications", UserNotificationListView, basename="notifications")
router.register(
    "notifications-archived",
    ArchivedNotificationListView,
    basename="notifications-archived",
)
router.register("reviews", ReviewViewSet, basename="reviews")
router.register("types-of-advertisement", TypesOfAdvertisementViewSet)

urlpatterns = router.urls
