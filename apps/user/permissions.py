from rest_framework.permissions import BasePermission
from apps.user.constants import ADMIN_ROLE_NAME

class IsAdminRole(BasePermission):
    """
    Grants access only to users with Admin role
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            hasattr(request.user, 'user_type') and 
            request.user.user_type.name == ADMIN_ROLE_NAME
        )