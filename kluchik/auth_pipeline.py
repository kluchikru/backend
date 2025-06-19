from django.contrib.auth import get_user_model


def associate_by_email_or_create(
    backend, uid, user=None, response=None, *args, **kwargs
):
    User = get_user_model()

    if user:
        # Пользователь уже найден (social_user), ничего не делаем
        return {"user": user}

    email = response.get("default_email") or response.get("emails", [None])[0]
    if not email:
        raise ValueError("Email not provided by provider")

    # Пытаемся найти пользователя по email
    try:
        user = User.objects.get(email=email)
        return {"user": user}
    except User.DoesNotExist:
        # Пользователя нет — создаём нового
        first_name = response.get("first_name", "")
        last_name = response.get("last_name", "")
        phone = (
            response.get("default_phone") or response.get("default_phone_number") or ""
        )

        user = User.objects.create(
            email=email,
            name=first_name,
            surname=last_name,
            phone_number=phone,
        )
        user.set_unusable_password()
        user.save()
        return {"user": user}


def save_user_profile(backend, user, response, *args, **kwargs):
    updated = False

    if backend.name == "yandex-oauth2":
        email = response.get("default_email") or response.get("emails", [None])[0]
        first_name = response.get("first_name", "")
        last_name = response.get("last_name", "")
        phone = (
            response.get("default_phone") or response.get("default_phone_number") or ""
        )

        if email and user.email != email:
            user.email = email
            updated = True
        if first_name and user.name != first_name:
            user.name = first_name
            updated = True
        if last_name and user.surname != last_name:
            user.surname = last_name
            updated = True
        if phone and user.phone_number != phone:
            user.phone_number = phone
            updated = True

        if updated:
            user.save()
