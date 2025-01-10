from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'},
        help_text="Password for the user"
    )

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'password', 'is_active']
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def create(self, validated_data):
        validated_data.pop('role', None)
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        # user.set_password(password)
        if password:
            user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        # if 'password' in validated_data:
        #     password = validated_data.pop('password')
        #     instance.set_password(password)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)

class UserRestoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = []