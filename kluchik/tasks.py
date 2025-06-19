from celery import shared_task
from datetime import date
from django.contrib.auth import get_user_model
from .models import Advertisement, Statistics

@shared_task
def collect_daily_statistics():
    User = get_user_model()
    user_count = User.objects.count()
    advertisement_count = Advertisement.objects.count()

    Statistics.objects.create(
        date=date.today(),
        user_count=user_count,
        advertisement_count=advertisement_count,
    )
