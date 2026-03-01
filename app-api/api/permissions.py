from rest_framework import permissions

class IsStaffUser(permissions.BasePermission):
    """
    Permite acesso apenas a usuários que são staff.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)


class IsOwnerOrStaff(permissions.BasePermission):
    """
    Permite acesso ao proprietário do objeto ou staff.
    """

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff