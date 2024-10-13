from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from .permissions import HasModelPermission
from .serializers import UserRegistrationSerializer, CustomTokenObtainPairSerializer, UserSerializer, ProductSerializer, \
    PermissionSerializer
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
    permission_classes = [IsAuthenticated, HasModelPermission]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]


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


