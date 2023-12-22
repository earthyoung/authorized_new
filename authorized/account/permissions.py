from rest_framework import permissions


class IsWriter(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsGroupUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in [obj.group.user_set]
