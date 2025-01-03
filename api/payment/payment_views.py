from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import PaymentMethod
from api.order.order_helper import updatePaymentStatus
from api.payment.payment_serializers import PaymentMethodSerializer
from api.payment.payment_viva_helper import check_payment


class PaymentMethodsView(generics.ListAPIView):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.AllowAny]


class CheckOrderPayment(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            check = check_payment(request.data)
            if check['statusId'] == 'F':
                request.data['status'] = 'PAID'
                updated_order = updatePaymentStatus(request.data)
                if updated_order:
                    check['order'] = updated_order

            return Response(check)
        except ValueError as ve:
            print(f"Validation error: {ve}")
            return Response({"error": str(ve)}, status=400)
        except Exception as e:
            print(f"Failed to handle payment: {e}")
            return Response({"error": str(e)}, status=500)

