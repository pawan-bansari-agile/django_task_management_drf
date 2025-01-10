from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import CustomUser
from .serializers import UserSerializer, UserRestoreSerializer
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from .permissions import IsAdminUserOrOwner
from rest_framework import status

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.filter(is_deleted=False)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        # elif self.action == 'list':
        elif self.action in ['list', 'restore_user', 'block_user', 'unblock_user']:
            return [IsAdminUser()]
        return super().get_permissions()
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.role != 'admin' and instance.id != request.user.id:
            return Response(
                {"detail": "You are not allowed to view details of other users."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.role != 'admin' and instance.id != request.user.id:
            return Response({"detail": "You can only update your own details."}, status=status.HTTP_403_FORBIDDEN)
        if 'role' in request.data and request.user.role != 'admin':
            return Response({"detail": "You cannot update the role."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # if request.user.role != 'admin' and instance.id != request.user.id:
        if request.user.role != 'admin':
            return Response({"detail": "You can only delete your own account."}, status=status.HTTP_403_FORBIDDEN)
        instance.is_active = False
        instance.save()
        return Response({"detail": "User has been deactivated."}, status=status.HTTP_204_NO_CONTENT)

    @extend_schema(responses={200: UserSerializer}, methods=["PATCH"])
    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @extend_schema(responses={200: UserSerializer}, methods=["POST"])
    @action(detail=True, methods=['post'], url_path='restore')
    def restore_user(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            return Response({"detail": "Only admins can restore users."}, status=status.HTTP_403_FORBIDDEN)
        instance = self.get_object()
        if not instance.is_active:
            instance.is_active = True
            instance.save()
            return Response({"detail": "User has been restored."})
        return Response({"detail": "User is already active."}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(description="Block a user to deactivate their access.")
    @action(detail=True, methods=['post'], url_path='block')
    def block_user(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            return Response({"detail": "Only admins can block users."}, status=status.HTTP_403_FORBIDDEN)
        instance = self.get_object()
        if instance.is_active:
            instance.is_active = False
            instance.save()
            return Response({"detail": "User has been blocked."}, status=status.HTTP_200_OK)
        return Response({"detail": "User is already blocked."}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(description="Unblock a user to reactivate their access.")
    @action(detail=True, methods=['post'], url_path='unblock')
    def unblock_user(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            return Response({"detail": "Only admins can unblock users."}, status=status.HTTP_403_FORBIDDEN)
        instance = self.get_object()
        if not instance.is_active:
            instance.is_active = True
            instance.save()
            return Response({"detail": "User has been unblocked."}, status=status.HTTP_200_OK)
        return Response({"detail": "User is already active."}, status=status.HTTP_400_BAD_REQUEST)