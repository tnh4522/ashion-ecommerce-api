from rest_framework import generics, permissions

from api.models import PaymentMethod
from api.payment.payment_serializers import PaymentMethodSerializer


class PaymentMethodsView(generics.ListAPIView):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.AllowAny]