import secrets
import string
from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, label='Confirm Password',
                                      style={'input_type': 'password'})

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'password', 'password2',
            'role', 'phone_number', 'date_of_birth', 'gender', 'profile_picture'
        )
        extra_kwargs = {'password': {'write_only': True}, 'password2': {'write_only': True},
                        'email': {'required': True}}

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=validated_data.get('role', 'BUYER'),
            phone_number=validated_data.get('phone_number', ''),
            date_of_birth=validated_data.get('date_of_birth'),
            gender=validated_data.get('gender'),
            profile_picture=validated_data.get('profile_picture')
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['role'] = user.role.name if user.role else None
        token['email'] = user.email
        token['id'] = user.id

        permissions = UserPermission.objects.filter(user=user).values_list('permission__model_name',
                                                                           'permission__action', 'allowed')
        token['permissions'] = [
            f"{model_name}:{action}" for model_name, action, allowed in permissions if allowed
        ]
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        data.update({
            'id': self.user.id,
            'role': self.user.role.name if self.user.role else None,
            'username': self.user.username,
            'email': self.user.email,
        })

        permissions = UserPermission.objects.filter(user=self.user).values_list('permission__model_name',
                                                                                'permission__action', 'allowed')
        data['permissions'] = [
            f"{model_name}:{action}" for model_name, action, allowed in permissions if allowed
        ]
        return data


class UserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False)
    social_links = serializers.JSONField(required=False)
    preferences = serializers.JSONField(required=False)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'phone_number', 'first_name', 'last_name',
            'date_of_birth', 'gender', 'profile_picture', 'bio',
            'social_links', 'preferences', 'role', 'password'
        )
        read_only_fields = ('id',)


class UserCreateSerializer(serializers.ModelSerializer):
    social_links = serializers.JSONField(required=False)
    preferences = serializers.JSONField(required=False)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'role', 'phone_number',
            'date_of_birth', 'gender', 'profile_picture',
            'first_name', 'last_name', 'bio', 'social_links', 'preferences'
        )
        extra_kwargs = {'username': {'required': True}}

    def create(self, validated_data):
        alphabet = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(alphabet) for _ in range(12))  # Tạo mật khẩu 12 ký tự ngẫu nhiên

        social_links = validated_data.pop('social_links', {})
        preferences = validated_data.pop('preferences', {})

        role = validated_data.get('role')

        user = User(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            role=role,
            phone_number=validated_data.get('phone_number', ''),
            date_of_birth=validated_data.get('date_of_birth'),
            gender=validated_data.get('gender'),
            profile_picture=validated_data.get('profile_picture'),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            bio=validated_data.get('bio', ''),
            social_links=social_links,
            preferences=preferences,
        )
        user.set_password(password)
        user.save()

        if role:
            role_permissions = RolePermission.objects.filter(role=role, allowed=True)

            user_permissions = [
                UserPermission(user=user, permission=rp.permission, allowed=True)
                for rp in role_permissions
            ]

            UserPermission.objects.bulk_create(user_permissions)

        self.generated_password = password

        return user


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            'id', 'name', 'parent', 'slug', 'description', 'image',
            'is_active', 'meta_title', 'meta_description', 'sort_order'
        )


class ProductSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False, allow_null=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, required=False, allow_null=True)

    class Meta:
        model = Product
        fields = [
            'id', 'user', 'name', 'sku', 'barcode', 'brand', 'description',
            'material', 'care_instructions', 'category', 'tags', 'price',
            'sale_price', 'start_sale_date', 'end_sale_date', 'stock', 'weight',
            'dimensions', 'sizes', 'colors', 'status', 'is_featured',
            'is_new_arrival', 'is_on_sale', 'main_image', 'video_url',
            'meta_title', 'meta_description', 'slug'
        ]
        read_only_fields = ('user', 'slug')

    def create(self, validated_data):
        user = self.context['request'].user
        tags = validated_data.pop('tags', [])
        product = Product.objects.create(user=user, **validated_data)
        product.tags.set(tags)
        return product


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


class UserPermissionSerializer(serializers.ModelSerializer):
    permission = PermissionSerializer(read_only=True)

    class Meta:
        model = UserPermission
        fields = ('id', 'permission', 'allowed')


class RoleSerializer(serializers.ModelSerializer):
    permissions = serializers.ListField(
        child=serializers.CharField(), write_only=True
    )

    class Meta:
        model = Role
        fields = ('id', 'name', 'description', 'permissions')

    def validate_permissions(self, value):
        permissions = []
        for perm_str in value:
            try:
                model_name, action = perm_str.split(':')
                permission = Permission.objects.get(model_name=model_name, action=action)
                permissions.append(permission)
            except (ValueError, Permission.DoesNotExist):
                raise serializers.ValidationError(f"Invalid permission: {perm_str}")
        return permissions

    def validate(self, attrs):
        attrs['permissions'] = self.validate_permissions(attrs.get('permissions', []))
        return attrs

    def create(self, validated_data):
        permissions = validated_data.pop('permissions', [])
        role = Role.objects.create(
            name=validated_data['name'],
            description=validated_data.get('description', '')
        )

        role_permissions = [
            RolePermission(role=role, permission=permission, allowed=True)
            for permission in permissions
        ]
        RolePermission.objects.bulk_create(role_permissions)

        return role
