from rest_framework_simplejwt.authentication import JWTAuthentication as BaseJWTAuth


def authenticate(username: str, password: str):
    from django.contrib.auth import get_user_model

    from .utils import resolve_user_by_phone

    User = get_user_model()
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        if "@" in username:
            try:
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                return None
        else:
            user = resolve_user_by_phone(username)
            if user is None:
                return None
    if user.check_password(password):
        return user
    return None


class JWTAuthentication(BaseJWTAuth):
    pass
