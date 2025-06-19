# backend

## Project setup
```
pip install -r requirements.txt
```

### Run the development server
```
python manage.py runserver
```

### Apply migrations for production
```
python manage.py makemigrations
python manage.py migrate
```

### Create a superuser
```
python manage.py createsuperuser
```

### Run tests
```
python manage.py test
```

### Collect static files
```
python manage.py collectstatic
```

### Dependencies
```
pip freeze > requirements.txt
```

### Redis - https://github.com/tporadowski/redis/releases
```
redis-cli
```

### Celery beat
```
celery -A project beat -l info
```

### Celery worker
```
celery -A project worker -l info --pool=solo
```

### Task init
```
python manage.py shell
from kluchik.tasks import task
task.delay()
```

### MailHog - https://github.com/mailhog/MailHog/releases
```
python manage.py shell
from django.core.mail import send_mail
send_mail(
    subject="Тестовое письмо",
    message="Это тест MailHog + Django!",
    from_email="test@example.com",
    recipient_list=["anyone@example.com"],
)
```
