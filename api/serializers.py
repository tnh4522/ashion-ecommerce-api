from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True, required=True, label='Confirm Password', style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'password',
            'password2',
            'role',
            'phone_number',
            'date_of_birth',
            'gender',
            'profile_picture',
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'password2': {'write_only': True},
            'email': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=validated_data.get('role', 'BUYER'),
            phone_number=validated_data.get('phone_number', ''),
            date_of_birth=validated_data.get('date_of_birth', None),
            gender=validated_data.get('gender', None),
            profile_picture=validated_data.get('profile_picture', None),
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['role'] = user.role
        token['email'] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Include additional user info in the response
        data.update({'role': self.user.role})
        data.update({'username': self.user.username})
        data.update({'email': self.user.email})
        return data


class UserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False)
    social_links = serializers.JSONField(required=False)
    preferences = serializers.JSONField(required=False)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'phone_number',
            'date_of_birth',
            'gender',
            'profile_picture',
            'bio',
            'social_links',
            'preferences',
        )
        read_only_fields = ('id',)
