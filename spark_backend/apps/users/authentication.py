import re

from django.contrib.auth import authenticate as django_authenticate
from rest_framework_simplejwt.authentication import JWTAuthentication as BaseJWTAuth


def authenticate(username: str, password: str):
    if re.match(r"[^@]+@[^@]+\.[^@]+", username):
        from django.contrib.auth import get_user_model

        user_model = get_user_model()
        try:
            user = user_model.objects.get(email=username)
        except user_model.DoesNotExist:
            return None
        if user.check_password(password):
            return user
        return None
    return django_authenticate(username=username, password=password)


class JWTAuthentication(BaseJWTAuth):
    pass
