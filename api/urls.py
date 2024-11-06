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
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/create/', CategoryCreateView.as_view(), name='category-create'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/create/', ProductCreateView.as_view(), name='product-create'),
    path('permissions/', PermissionListView.as_view(), name='permissions'),
    path('permissions/create/', CreateUserPermissionView.as_view(), name='create_permission'),
    path('permissions/user/<int:user_id>/', UserPermissionsView.as_view(), name='user_permissions'),
    path('permissions/user/<int:user_id>/update/', UpdateUserPermissionsView.as_view(), name='update_user_permissions'),
    path('roles/', RoleListCreateView.as_view(), name='role-list-create'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.MEDIA_ROOT)
