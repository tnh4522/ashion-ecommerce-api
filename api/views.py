from django_filters.rest_framework import DjangoFilterBackend
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
from rest_framework.parsers import MultiPartParser, FormParser

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


# Category Management
class CategoryCreateView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # permission_classes = [HasRolePermission]
    permission_classes = [permissions.AllowAny]
    model_name = 'Category'
    action = 'add'


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

    # Update Category
class CategoryUpdateView(APIView):
    # permission_classes = [HasRolePermission]
    permission_classes = [permissions.AllowAny]

    def put(self, request, pk, *args, **kwargs):
        try:
            category = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryDetailView(APIView):
    #permission_classes = [HasRolePermission]
    permission_classes = [permissions.AllowAny]
    def get(self, request, pk, *args, **kwargs):
        try:
            category = Category.objects.get(pk=pk)
            serializer = CategorySerializer(category)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

# Delete Category
class CategoryDeleteView(APIView):
    #permission_classes = [HasRolePermission]
    permission_classes = [permissions.AllowAny]
    def delete(self, request, pk, format=None):
        try:
            category = Category.objects.get(pk=pk)
            category.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

# Product Management
class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
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


# views.py

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


class RoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

    # permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    # model_name = 'Role'

    def get_action(self):
        if self.request.method == 'GET':
            return 'view'
        elif self.request.method in ['PUT', 'PATCH']:
            return 'change'
        elif self.request.method == 'DELETE':
            return 'delete'
        else:
            return None

    def get_permissions(self):
        self.action = self.get_action()
        return super().get_permissions()


class StockCreateView(generics.CreateAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    # permission_classes = [permissions.IsAuthenticated]


# Update, delete, or get specific stock
class StockUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    # permission_classes = [permissions.IsAuthenticated]


# List all stocks
class StockListView(generics.ListAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    # permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name', 'is_active', 'location']
    search_fields = ['name', 'description', 'location']
    ordering_fields = ['name', 'created_at']
    pagination_class = StandardResultsSetPagination


# Create new stock product entry
class StockProductCreateView(generics.CreateAPIView):
    queryset = StockProduct.objects.all()
    serializer_class = StockProductSerializer
    # permission_classes = [permissions.IsAuthenticated]


# Update, delete, or get specific stock product
class StockProductUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StockProduct.objects.all()
    serializer_class = StockProductSerializer
    # permission_classes = [permissions.IsAuthenticated]


# List all stock products
class StockProductListView(generics.ListAPIView):
    queryset = StockProduct.objects.all()
    serializer_class = StockProductSerializer
    # permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product__name', 'quantity']
    search_fields = ['product__name']
    ordering_fields = ['quantity', 'updated_at']
    pagination_class = StandardResultsSetPagination

#List all orders
class OrderListView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['created_at', 'total_price']
    pagination_class = StandardResultsSetPagination


class OrderCreateAPIView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


# Store Management Views
# Create Store
class StoreCreateView(generics.CreateAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer

    # permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    # model_name = 'Store'
    # action = 'add'

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


# List All Stores
class StoreListView(generics.ListAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['store_name', 'is_verified']
    search_fields = ['store_name', 'store_description']
    ordering_fields = ['store_name', 'rating', 'total_sales']
    pagination_class = StandardResultsSetPagination


# Store Detail, Update, Delete
class StoreDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer

    # permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    # model_name = 'Store'

    def get_action(self):
        if self.request.method == 'GET':
            return 'view'
        elif self.request.method in ['PUT', 'PATCH']:
            return 'change'
        elif self.request.method == 'DELETE':
            return 'delete'
        else:
            return None


# Brand Management Views
# Create Brand
class BrandCreateView(generics.CreateAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    # permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    # model_name = 'Brand'
    # action = 'add'


# List All Brands
class BrandListView(generics.ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['brand_name', 'is_verified']
    search_fields = ['brand_name', 'brand_description']
    ordering_fields = ['brand_name', 'created_at']
    pagination_class = StandardResultsSetPagination


# Brand Detail, Update, Delete
class BrandDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    # permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    # model_name = 'Brand'

    def get_action(self):
        if self.request.method == 'GET':
            return 'view'
        elif self.request.method in ['PUT', 'PATCH']:
            return 'change'
        elif self.request.method == 'DELETE':
            return 'delete'
        else:
            return None
        
class AddressCreateView(generics.CreateAPIView):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
       # If this is the first address or marked as default, handle default address logic
       if serializer.validated_data.get('default', False) or not Address.objects.filter(user=self.request.user).exists():
           # Set all other addresses of the same type to non-default
           Address.objects.filter(
               user=self.request.user,
               address_type=serializer.validated_data.get('address_type', 'SHIPPING')
           ).update(default=False)
       
       serializer.save(user=self.request.user)

class AddressListView(generics.ListAPIView):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
       return Address.objects.filter(user=self.request.user)