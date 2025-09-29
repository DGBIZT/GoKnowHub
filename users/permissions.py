from rest_framework.permissions import BasePermission
from rest_framework import status
from rest_framework.exceptions import PermissionDenied

class IsModer(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='moderators').exists()

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj.owner == request.user

class IsModerOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name='moderators').exists():
            if request.method in ['GET', 'PUT', 'PATCH']:
                return True
            raise PermissionDenied("У модераторов нет прав на удаление и создание")
        return obj.owner == request.user
