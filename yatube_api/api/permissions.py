from rest_framework import permissions


class AuthorOrReadOnly(permissions.BasePermission):
    """
    Класс разрешения, который позволяет авторам редактировать свои собственные
    объекты, а всем остальным - читать их.
    """
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class ReadOnly(permissions.BasePermission):
    """
    Класс разрешения, который разрешает только
    безопасные методы (GET, HEAD, OPTIONS).
    """
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
