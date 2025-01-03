from django.urls import path
from .payment_views import *

urlpatterns = [
    path('methods/', PaymentMethodsView.as_view(), name='order-list'),
    path('check/', CheckOrderPayment.as_view(), name='check-payment'),
]