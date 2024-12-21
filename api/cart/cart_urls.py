from django.urls import path
from .cart_views import CartView, CartItemUpdateDeleteView

urlpatterns = [
    path('create/', CartView.as_view(), name='cart'),
    path('detail/', CartView.as_view(), name='cart-detail'),
    path('items/<int:item_id>/', CartItemUpdateDeleteView.as_view(), name='cart-item-update-delete'),
]
