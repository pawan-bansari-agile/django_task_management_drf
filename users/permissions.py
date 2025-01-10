from rest_framework.permissions import BasePermission

class IsAdminUserOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Admins can access everything
        if request.user.role == 'admin':
            return True
        # Users can access only their own object
        return obj.id == request.user.id
