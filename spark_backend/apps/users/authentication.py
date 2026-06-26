from rest_framework_simplejwt.authentication import JWTAuthentication as BaseJWTAuth


def authenticate(username: str, password: str):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        try:
            if "@" in username:
                user = User.objects.get(email=username)
            else:
                user = User.objects.get(phone_number=username)
        except User.DoesNotExist:
            return None
    if user.check_password(password):
        return user
    return None


class JWTAuthentication(BaseJWTAuth):
    pass
