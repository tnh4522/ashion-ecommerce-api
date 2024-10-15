from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from .permissions import HasModelPermission, IsAdmin
from .serializers import UserRegistrationSerializer, CustomTokenObtainPairSerializer, UserSerializer, ProductSerializer, \
    PermissionSerializer, UserCreateSerializer
from .models import User, Product, Permission
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from .models import Category
from .serializers import CategorySerializer
import logging

logger = logging.getLogger(__name__)


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'user': UserRegistrationSerializer(
                    user, context=self.get_serializer_context()
                ).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


class UserLoginView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = CustomTokenObtainPairSerializer


class UserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserManagerView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            user = request.user
        user.delete()
        return Response({'detail': 'User deleted successfully.'}, status=status.HTTP_200_OK)


class UserRoleView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            user = request.user
        return Response({'role': user.role})

    def put(self, request, *args, **kwargs):
        if request.user.role != 'ADMIN':
            return Response({'detail': 'Only administrators can update roles.'}, status=status.HTTP_403_FORBIDDEN)

        user_id = self.kwargs.get('user_id')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        role = request.data.get('role')
        if role not in [choice[0] for choice in User.ROLE_CHOICES]:
            return Response({'detail': 'Invalid role.'}, status=status.HTTP_400_BAD_REQUEST)

        user.role = role
        user.save()
        return Response({'detail': 'Role updated successfully.'}, status=status.HTTP_200_OK)


class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = UserCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

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


class StandardResultsSetPagination(PageNumberPagination):
    page_size_query_param = 'page_size'


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'gender']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'email', 'date_joined', 'first_name', 'last_name']
    pagination_class = StandardResultsSetPagination


class CategoryCreateView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        logger.debug("Fetching all categories")
        return super().get_queryset()


class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__name', 'price', 'stock']
    search_fields = ['name', 'category__name']
    ordering_fields = ['name', 'price', 'stock']
    pagination_class = StandardResultsSetPagination


class ProductUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, HasModelPermission]


class CreatePermissionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.role != 'ADMIN':
            return Response({'detail': 'Only administrators can create permissions.'}, status=status.HTTP_403_FORBIDDEN)

        if isinstance(request.data, list):
            serializer = PermissionSerializer(data=request.data, many=True)
        else:
            serializer = PermissionSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPermissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        permissions = Permission.objects.filter(user=user)
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateUserPermissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        user = request.user
        if user.role != 'ADMIN':
            return Response({'detail': 'Only administrators can update permissions.'}, status=status.HTTP_403_FORBIDDEN)

        target_user = User.objects.filter(id=user_id).first()
        if not target_user:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        if isinstance(request.data, list):
            for permission_data in request.data:
                permission_data['user'] = target_user.id

                permission_instance = Permission.objects.filter(
                    user=target_user,
                    model_name=permission_data['model_name'],
                    action=permission_data['action']
                ).first()

                serializer = PermissionSerializer(instance=permission_instance, data=permission_data)

                if serializer.is_valid():
                    serializer.save()
                else:
                    logger.error(f"Validation failed for permission: {serializer.errors}")
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'Permissions updated successfully.'}, status=status.HTTP_200_OK)
        else:
            request.data['user'] = target_user.id

            permission_instance = Permission.objects.filter(
                user=target_user,
                model_name=request.data['model_name'],
                action=request.data['action']
            ).first()

            serializer = PermissionSerializer(instance=permission_instance, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                logger.error(f"Validation failed for permission: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
