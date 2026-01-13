from rest_framework.permissions import BasePermission


class IsAuthor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["AUTHOR", "ADMIN"]


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "author"):
            return obj.author == request.user
        if hasattr(obj, "user"):
            return obj.user == request.user
        return False


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True
        if hasattr(obj, "author"):
            return obj.author == request.user
        if hasattr(obj, "user"):
            return obj.user == request.user
        return False
