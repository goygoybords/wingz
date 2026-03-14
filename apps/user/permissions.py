from rest_framework.permissions import BasePermission

class IsAdminRole(BasePermission):
    """
    Grants access only to users with Admin users
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            hasattr(request.user, 'user_type') and 
            request.user.user_type.name == "Admin"
        )