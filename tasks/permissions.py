from rest_framework.permissions import BasePermission

# class IsAdminOrAssignedUser(BasePermission):
#     def has_object_permission(self, request, view, obj):
#         if request.user.role == 'admin':
#             return True
#         return obj.assigned_to == request.user
class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

class IsTaskAssignee(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.assigned_to == request.user

class CanUpdateStatusToCompleted(BasePermission):
    def has_object_permission(self, request, view, obj):
        # return obj.assigned_to == request.user and obj.status == 'ongoing'
        # Allow admins to update the status of any task
        if request.user.role == 'admin':
            return True
        # # Allow assigned users to update the status from 'ongoing' to 'completed'
        # return (
        #     request.user == obj.assigned_to and
        #     obj.status == 'ongoing' and
        #     request.data.get('status') == 'completed'
        # )
        if request.user.role == 'user':
            new_status = request.data.get('status')
            return obj.status in ['ongoing', 'completed'] and new_status in ['ongoing', 'completed']

        return False