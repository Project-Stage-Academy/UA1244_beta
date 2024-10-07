from rest_framework import serializers
from .models import User, Role

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('role_id', 'role_name')

class RegisterUserSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(many=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('user_id', 'user_name', 'first_name', 'last_name', 'email', 'user_phone', 'roles', 'password', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

    def create(self, validated_data):
        # Вилучаємо дані про ролі та пароль
        roles_data = validated_data.pop('roles', [])
        password = validated_data.pop('password')
        
       
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()  

        for role_data in roles_data:
            role_name = role_data.get('role_name')
            if role_name:  
                role, created = Role.objects.get_or_create(role_name=role_name)
                user.roles.add(role)
        
        return user

class UserSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(many=True)

    class Meta:
        model = User
        fields = ('user_id', 'user_name', 'first_name', 'last_name', 'email', 'user_phone', 'roles', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')