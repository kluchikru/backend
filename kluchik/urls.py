from rest_framework import routers

from .views import *


# Регистрация ViewSet'ов в роутере
router = routers.DefaultRouter()
router.register("users", UsersViewSet)
router.register("types-of-advertisement", TypesOfAdvertisementViewSet)

# Получение маршрутов
urlpatterns = router.urls
