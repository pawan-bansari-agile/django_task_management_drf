from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'name', 'description', 'assigned_to', 'created_at', 'updated_at', 'status', 'attachments']
        # fields = '__all__'
        # read_only_fields = ['created_at', 'updated_at']


    def validate_assigned_to(self, value):
        if value.role == 'admin':
            raise serializers.ValidationError("Tasks can only be assigned to staff users.")
        return value

    def validate_attachments(self, value):
        if not value:
            return value
        if isinstance(value, list):
            for file in value:
                if not file.content_type.startswith(('image/', 'video/', 'application/')):
                    raise serializers.ValidationError("Attachments must be an image, video, or document.")
        return value


class TaskStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['status']

    def validate_status(self, value):
        task = self.instance
        user = self.context['request'].user

        if user.role == 'user' and value not in ['ongoing', 'completed']:
            raise serializers.ValidationError("You can only update status to 'ongoing' or 'completed'.")
        
        # Prevent users from transitioning statuses incorrectly
        if user.role == 'user' and task.status == 'draft':
            raise serializers.ValidationError("You cannot update a task with 'draft' status.")
        if user.role == 'user' and task.status == 'archived':
            raise serializers.ValidationError("You cannot update a task with 'archived' status.")

        return value