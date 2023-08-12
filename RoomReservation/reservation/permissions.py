# permissions.py
from rest_framework import permissions

class IsManagerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow read-only permissions for all users (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        # Check if the user is manager
        return request.user.groups.filter(name = 'manager').exists()

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
