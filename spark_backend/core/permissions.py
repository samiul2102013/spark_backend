from rest_framework.permissions import BasePermission


class IsCoordinator(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "coordinator"


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"


class IsGovernment(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "government"


class IsResident(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "resident"


class IsCoordinatorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return request.user.role in ("coordinator", "admin")
