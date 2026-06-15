from rest_framework_simplejwt.authentication import JWTAuthentication as BaseJWTAuth


def authenticate(username: str, password: str):
    from django.contrib.auth import get_user_model

    user_model = get_user_model()
    try:
        user = user_model.objects.get(username=username)
    except user_model.DoesNotExist:
        return None
    if user.check_password(password):
        return user
    return None


class JWTAuthentication(BaseJWTAuth):
    pass
