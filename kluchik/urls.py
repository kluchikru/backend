from rest_framework import routers

from .views import *


router = routers.DefaultRouter()
router.register("users", UsersViewSet)
router.register("types-of-advertisement", TypesOfAdvertisementViewSet)
urlpatterns = router.urls
