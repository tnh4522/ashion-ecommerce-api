
from django.urls import path, include

from .brand.brand_views import *
from .customer.customer_views import *
from .stock.stock_views import *
from .store.store_views import *
from .order.order_views import *
from .views import *
from .product.variant_views import *
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('activity/', include('api.activity.activity_urls')),
    path('register', UserRegistrationView.as_view(), name='register'),
    path('login', UserLoginView.as_view(), name='login'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserDetailView.as_view(), name='user-detail'),
    path('me/store/', GetStoreByUser.as_view(), name='user-store'),
    path('user/<int:pk>/', UserManagerView.as_view(), name='user-manager'),
    path('users/<int:pk>/role/', UserRoleView.as_view(), name='user-role'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('create-user/', UserCreateView.as_view(), name='admin-create-user'),
    path('users/create-password/', CreatePasswordView.as_view(), name='create-password'),
    path('categories/', include('api.category.categories_urls')),
    path('product/', include('api.product.product_urls')),
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
    path('brand/', include('api.brand.brand_urls')),
    path('customer/', include('api.customer.customer_urls')),
    path('address/', include('api.address.address_urls')),
]
