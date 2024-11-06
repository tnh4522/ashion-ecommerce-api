from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions
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


# User Login
class UserLoginView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = CustomTokenObtainPairSerializer


# User Detail (Self)
class UserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
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

        # Lấy mật khẩu đã được tạo ngẫu nhiên từ serializer
        generated_password = serializer.generated_password

        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                'user': serializer.data,
                'generated_password': generated_password,
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )


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


# Category Management
class CategoryCreateView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [HasRolePermission]
    model_name = 'Category'
    action = 'add'


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


# Product Management
class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [HasRolePermission]
    model_name = 'Product'
    action = 'add'


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__name', 'price', 'stock']
    search_fields = ['name', 'category__name']
    ordering_fields = ['name', 'price', 'stock']
    pagination_class = StandardResultsSetPagination


class ProductUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [HasRolePermission]
    model_name = 'Product'
    action = 'change'


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
            permission_data['user'] = target_user.id
            instance = UserPermission.objects.filter(
                user=target_user, permission__model_name=permission_data['model_name'],
                permission__action=permission_data['action']
            ).first()

            serializer = PermissionSerializer(instance=instance, data=permission_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response({'detail': 'Permissions updated successfully.'}, status=status.HTTP_200_OK)


class PermissionListView(generics.ListAPIView):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    # permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    # model_name = 'Permission'
    # action = 'view'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['model_name', 'action']
    search_fields = ['model_name', 'action']
    ordering_fields = ['model_name', 'action']
    pagination_class = StandardResultsSetPagination


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
