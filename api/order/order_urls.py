from django.urls import path
from .order_views import *

urlpatterns = [
    path('list/', OrderListView.as_view(), name='order-list'),
    path('create/', OrderCreateView.as_view(), name='order-create'),
    path('detail/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('view/<int:pk>/', OrderDetailForView.as_view(), name='order-view'),
    path('user/', OrderByUserView.as_view(), name='order-by-user'),
    path('customer/<int:customer_id>/', GetOrdersByCustomerID.as_view(), name='order-by-customer'),
]