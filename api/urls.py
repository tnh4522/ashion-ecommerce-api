from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('register', UserRegistrationView.as_view(), name='register'),
    path('login', UserLoginView.as_view(), name='login'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserDetailView.as_view(), name='user-detail'),
    path('user/<int:pk>/', UserManagerView.as_view(), name='user-manager'),
    path('users/<int:pk>/role/', UserRoleView.as_view(), name='user-role'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('create-user/', UserCreateView.as_view(), name='admin-create-user'),
    path('users/create-password/', CreatePasswordView.as_view(), name='create-password'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/create/', CategoryCreateView.as_view(), name='category-create'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('categories/<int:pk>/update/', CategoryUpdateView.as_view(), name='category-update'),
    path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category-delete'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/create/', ProductCreateView.as_view(), name='product-create'),
    # path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='product-update'),
    # path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),
    path('permissions/', PermissionListView.as_view(), name='permissions'),
    path('permissions/create/', CreateUserPermissionView.as_view(), name='create_permission'),
    path('permissions/user/<int:user_id>/', UserPermissionsView.as_view(), name='user_permissions'),
    path('permissions/user/<int:user_id>/update/', UpdateUserPermissionsView.as_view(), name='update_user_permissions'),
    path('roles/', RoleListCreateView.as_view(), name='role-list-create'),
    path('roles/<int:pk>/', RoleDetailView.as_view(), name='role-detail'),
    path('stocks/', StockListView.as_view(), name='stock-list'),
    path('stocks/create/', StockCreateView.as_view(), name='stock-create'),
    path('stocks/<int:pk>/', StockUpdateDeleteView.as_view(), name='stock-update-delete'),
    path('stock-products/', StockProductListView.as_view(), name='stock-product-list'),
    path('stock-products/create/', StockProductCreateView.as_view(), name='stock-product-create'),
    path('stock-products/<int:pk>/', StockProductUpdateDeleteView.as_view(), name='stock-product-update-delete'),
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/create/', OrderCreateView.as_view(), name='order-create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('stores/create/', StoreCreateView.as_view(), name='store-create'),
    path('stores/', StoreListView.as_view(), name='store-list'),
    path('stores/<int:pk>/', StoreDetailView.as_view(), name='store-update-delete'),
    path('brands/', BrandListView.as_view(), name='brand-list'),
    path('brands/create/', BrandCreateView.as_view(), name='brand-create'),
    path('brands/<int:pk>/', BrandDetailView.as_view(), name='brand-update-delete'),
    path('customers/', CustomerManagerView.as_view(), name='customer-manager'),
    path('customer/<int:pk>/', CustomerDetailView.as_view(), name='customer-detail'),
    path('customer/create/', CustomerManagerView.as_view(), name='customer-create'),
    path('address/', AddressListView.as_view(), name='address-list'),
    path('address/create/', AddressCreateView.as_view(), name='address-create'),
    # path('address/<int:user_id>/', AddressListView.as_view(), name='address-list-user'),
    path('address/<int:pk>/', AddressDetailView.as_view(), name='address-detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.MEDIA_ROOT)
