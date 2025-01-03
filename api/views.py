from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse
from rest_framework import filters, permissions
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from .serializers import *
from .models import *
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, status
from rest_framework.response import Response
from .models import User
from .serializers import UserCreateSerializer
from .permissions import HasRolePermission
from rest_framework.permissions import IsAuthenticated

from .store.store_serializers import StoreSerializer


# Pagination Setup
class StandardResultsSetPagination(PageNumberPagination):
    page_size_query_param = 'page_size'


# User Registration
class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserRegistrationSerializer(user, context=self.get_serializer_context()).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


@extend_schema_view(
    post=extend_schema(
        responses={200: ResponseLoginSerializer}
    )
)
class UserLoginView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = CustomTokenObtainPairSerializer


# User Detail (Self)
class UserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserViewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# User Manager (Admin)
class UserManagerView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    # model_name = 'User'
    # action = 'change'


class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer

    # permission_classes = [IsAuthenticated, HasRolePermission]
    # model_name = 'User'
    # action = 'add'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                'user': serializer.data
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )


# View for creating password
class CreatePasswordView(generics.CreateAPIView):
    permissions_classes = [IsAuthenticated]
    serializer_class = CreatePasswordSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({'detail': f'Password created successfully for user {user.username}'},
                        status=status.HTTP_201_CREATED)


# User List (Admin)
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [HasRolePermission]
    # model_name = 'User'
    # action = 'view'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'gender']
    search_fields = ['username', 'email']
    ordering_fields = ['username', 'email', 'date_joined']
    pagination_class = StandardResultsSetPagination


# Role Management
class UserRoleView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # permission_classes = [HasRolePermission]
    # model_name = 'User'
    # action = 'change'

    def put(self, request, *args, **kwargs):
        role = request.data.get('role')
        user = self.get_object()

        if role not in [choice[0] for choice in User.ROLE_CHOICES]:
            return Response({'detail': 'Invalid role.'}, status=status.HTTP_400_BAD_REQUEST)

        user.role = role
        user.save()
        return Response({'detail': 'Role updated successfully.'}, status=status.HTTP_200_OK)


# User Permission Management
class CreateUserPermissionView(APIView):
    # permission_classes = [HasRolePermission]
    # model_name = 'UserPermission'
    # action = 'add'

    def post(self, request):
        serializer = PermissionSerializer(data=request.data, many=isinstance(request.data, list))
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserPermissionsView(APIView):
    # permission_classes = [HasRolePermission]
    # model_name = 'UserPermission'
    # action = 'view'

    def get(self, request, user_id):
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        user_permissions = UserPermission.objects.filter(user=user)
        serializer = UserPermissionSerializer(user_permissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateUserPermissionsView(APIView):
    # permission_classes = [HasRolePermission]
    # model_name = 'UserPermission'
    # action = 'change'

    def post(self, request, user_id):
        target_user = User.objects.filter(id=user_id).first()
        if not target_user:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data if isinstance(request.data, list) else [request.data]

        for permission_data in data:
            up_id = permission_data.get('id')
            allowed = permission_data.get('allowed')

            if up_id is None:
                return Response({'detail': 'Permission ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                instance = UserPermission.objects.get(id=up_id, user=target_user)
            except UserPermission.DoesNotExist:
                return Response({'detail': f'UserPermission with ID {up_id} not found for this user.'},
                                status=status.HTTP_404_NOT_FOUND)

            instance.allowed = allowed
            instance.save()

        return Response({'detail': 'Permissions updated successfully.'}, status=status.HTTP_200_OK)


class PermissionListView(generics.ListAPIView):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    # permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    # model_name = 'Permission'
    # action = 'view'


class RoleListCreateView(generics.ListCreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    # permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    # model_name = 'Role'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name']
    search_fields = ['name', 'description']
    ordering_fields = ['name']
    pagination_class = StandardResultsSetPagination

    def get_action(self):
        if self.request.method == 'GET':
            return 'view'
        elif self.request.method == 'POST':
            return 'add'
        else:
            return None

    def get_permissions(self):
        self.action = self.get_action()
        return super().get_permissions()


class RoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

    # permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    # model_name = 'Role'


class UpdateRolePermissionsView(APIView):
    """
    API view to update permissions of a specific role.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=RolePermissionUpdateSerializer,
        responses={
            200: OpenApiResponse(description="Permissions updated successfully."),
            400: OpenApiResponse(description="Invalid data."),
            401: OpenApiResponse(description="Unauthorized."),
            404: OpenApiResponse(description="Role not found."),
        },
        summary="Update Permissions of a Role",
        description="Endpoint to update the permissions associated with a specific role."
    )
    def post(self, request, role_id):
        """
        Update the permissions of the role identified by role_id.
        Expects a JSON payload with a 'permissions' field containing a list of permission strings.
        """
        role = get_object_or_404(Role, id=role_id)

        self.check_object_permissions(request, role)

        serializer = RolePermissionUpdateSerializer(data=request.data)
        if serializer.is_valid():
            valid_permissions = serializer.validated_data['permissions']
            serializer.update_permissions(role, valid_permissions)
            return Response({'detail': 'Permissions updated successfully.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetStoreByUser(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        store = Store.objects.filter(user=request.user).first()
        if not store:
            return Response({'detail': 'Store not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = StoreSerializer(store)
        return Response(serializer.data, status=status.HTTP_200_OK)
