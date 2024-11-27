from rest_framework import serializers
from ..models import User, UserPermission
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, label='Confirm Password', style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password2', 'role', 'phone_number', 'date_of_birth', 'gender', 'profile_picture')
        extra_kwargs = {'password': {'write_only': True}, 'password2': {'write_only': True}, 'email': {'required': True}}

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        role = validated_data.pop('role', None)
        user = User.objects.create_user(**validated_data)
        if role:
            user.role = role
            user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['role'] = user.role.name if user.role else None
        token['email'] = user.email
        token['id'] = user.id
        permissions = UserPermission.objects.filter(user=user).values_list('permission__model_name', 'permission__action', 'allowed')
        token['permissions'] = [f"{model_name}:{action}" for model_name, action, allowed in permissions if allowed]
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({'id': self.user.id, 'role': self.user.role.name if self.user.role else None, 'username': self.user.username, 'email': self.user.email})
        permissions = UserPermission.objects.filter(user=self.user).values_list('permission__model_name', 'permission__action', 'allowed')
        data['permissions'] = [f"{model_name}:{action}" for model_name, action, allowed in permissions if allowed]
        return data
