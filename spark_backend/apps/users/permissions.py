from rest_framework.permissions import BasePermission


class IsRole(BasePermission):
    def __init__(self, *roles: str):
        self.roles = roles

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in self.roles


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"


class IsResidentOrCoordinator(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ("resident", "coordinator")
