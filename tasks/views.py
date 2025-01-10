from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Attachment, Task
from .serializers import TaskSerializer, TaskStatusUpdateSerializer
from .permissions import IsAdminUser, IsTaskAssignee, CanUpdateStatusToCompleted

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    # permission_classes = [IsAuthenticated]

    def get_permissions(self):
        # if self.action in ['list', 'retrieve', 'filter_tasks', 'task_statistics']:
        #     return [IsAuthenticated()]
        # elif self.action in ['create', 'update', 'partial_update', 'destroy', 'archive_task']:
        #     return [IsAdminOrAssignedUser()]
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'archive_task']:
            return [IsAdminUser()]
        
        # if self.action in ['retrieve', 'list', 'filter_tasks', 'task_statistics']:
        if self.action in ['retrieve', 'list']:
            return [IsAuthenticated()]

        if self.action == 'update_status':
            return [CanUpdateStatusToCompleted()]

        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user

        if self.request.user.role == 'admin':
            return Task.objects.all()

        return Task.objects.filter(assigned_to=user, status__in=['draft', 'ongoing', 'completed'])
    
    def perform_create(self, serializer):
        assigned_user = serializer.validated_data.get('assigned_to')
        
        attachments = self.request.FILES.getlist('attachments')

        if assigned_user.role != 'user':
            raise ValueError("Tasks can only be assigned to users with the 'user' role.")

        # serializer.save()
        task = serializer.save()
        for attachment in attachments:
            Attachment.objects.create(file=attachment, task=task)

    @action(detail=False, methods=['get'], url_path='statistics')
    def task_statistics(self, request):
        if request.user.role != 'user':
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)

        tasks = self.get_queryset()

        stats = {
            'draft': tasks.filter(status='draft').count(),
            'ongoing': tasks.filter(status='ongoing').count(),
            'completed': tasks.filter(status='completed').count()
        }

        return Response(stats, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='filter')
    def filter_tasks(self, request):
        filters = {key: value for key, value in request.query_params.items() if key in ['status', 'assigned_to']}

        tasks = self.get_queryset().filter(**filters)

        serializer = self.get_serializer(tasks, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='archive')
    def archive_task(self, request, pk=None):
        task = self.get_object()
        # try:
        #     task.archive()
        #     return Response({"detail": "Task archived successfully."}, status=status.HTTP_200_OK)
        # except ValueError as e:
        #     return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        if task.status != 'completed':
            return Response({"detail": "Only completed tasks can be archived."}, status=status.HTTP_400_BAD_REQUEST)

        task.status = 'archived'

        task.save()

        return Response({"detail": "Task archived successfully."}, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        """Restrict PATCH/PUT for non-admin users."""
        if request.user.role == 'user':
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    # @action(detail=True, methods=['patch'], url_path='update-status')
    # def update_status(self, request, pk=None):
    #     task = self.get_object()
    #     print('task', task)

    #     # if request.user.role == 'user' and task.assigned_to != request.user:
    #     #     return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)

    #     # if task.status != 'ongoing':
    #     #     return Response({"detail": "Only tasks with status 'ongoing' can be updated to 'completed'."}, status=status.HTTP_400_BAD_REQUEST)

    #     if request.user.role == 'user':
    #         print('inside the first if statement')
    #         new_status = request.data.get('status')
    #         if task.status not in ['ongoing', 'completed'] or new_status not in ['ongoing', 'completed']:
    #             print('inside the second if statement')
    #             return Response(
    #                 {"detail": "You can only update the status between 'ongoing' and 'completed'."},
    #                 status=status.HTTP_403_FORBIDDEN,
    #             )

    #     serializer = TaskStatusUpdateSerializer(task, data=request.data, partial=True)

    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_200_OK)

    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @action(detail=True, methods=['patch'], url_path='update-status')
    def update_status(self, request, pk=None):
        try:
            # Retrieve the task instance
            task = self.get_object()
            print(f"Task Retrieved: {task}")
            print(f"Current Task Status: {task.status}")

            # Extract the new status from request data
            new_status = request.data.get('status', '').strip()
            print(f"New Status from Request: {new_status}")

            # Check if the 'status' field is provided
            if not new_status:
                return Response(
                    {"detail": "The 'status' field is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validate that the new status is allowed
            allowed_statuses = ['draft', 'ongoing', 'completed', 'archived']
            if new_status not in allowed_statuses:
                print(f"Invalid status value: {new_status}")
                return Response(
                    {
                        "detail": f"Invalid status value: '{new_status}'. "
                                  f"Allowed values are {', '.join(allowed_statuses)}."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Role-specific validation
            if request.user.role == 'user':
                print("Inside user role validation")
                if task.status not in ['ongoing', 'completed']:
                    print(f"User cannot modify task with status '{task.status}'")
                    return Response(
                        {
                            "detail": f"Users can only update tasks with status "
                                      f"'ongoing' or 'completed', not '{task.status}'."
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )

                if new_status not in ['ongoing', 'completed']:
                    print(f"User trying to set an invalid status '{new_status}'")
                    return Response(
                        {"detail": "You can only update the status between 'ongoing' and 'completed'."},
                        status=status.HTTP_403_FORBIDDEN,
                    )

            # Serialize and validate the task for partial update
            serializer = TaskStatusUpdateSerializer(task, data={'status': new_status}, partial=True, context={'request': request})
            if serializer.is_valid():
                print("Serializer is valid, saving task")
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                print(f"Serializer validation failed: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Task.DoesNotExist:
            print("Task not found")
            return Response(
                {"detail": "Task not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            print(f"Unexpected error: {e}")
            import traceback
            traceback.print_exc() 
            return Response(
                {"detail": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


