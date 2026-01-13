from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class IsAuthor(BasePermission):
    def has_permission(self, request: Request, view: APIView) -> bool:
        return bool(request.user.is_authenticated and request.user.role in ["AUTHOR", "ADMIN"])


class IsOwner(BasePermission):
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        if hasattr(obj, "author"):
            return obj.author == request.user
        if hasattr(obj, "user"):
            return obj.user == request.user
        return False


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True
        if hasattr(obj, "author"):
            return obj.author == request.user
        if hasattr(obj, "user"):
            return obj.user == request.user
        return False
