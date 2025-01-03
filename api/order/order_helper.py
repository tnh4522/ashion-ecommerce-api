from flask.json import jsonify

from api.models import PaymentMethod, Order
from api.payment.payment_viva_helper import process_payment


def handlePayment(request, order_data):
    try:
        payment_methoad = PaymentMethod.objects.get(method_type=request.data['payment_method'])
        module_payment = payment_methoad.module_payment
        if module_payment.module_name == 'vivapayments':
            return process_payment(request.data, order_data)
    except Exception as e:
        print(f"Failed to handle payment: {e}")
        return jsonify({"error": str(e)}), 500


def updatePaymentStatus(data):
    try:
        if 'orderNumber' not in data or not data['orderNumber']:
            raise ValueError("Missing 'order_number' in request data.")

        order = Order.objects.get(order_number=data['orderNumber'])

        order.payment_status = data['status']
        order.save()

        return {
            "order_number": order.order_number,
            "payment_status": order.payment_status,
            "updated_at": order.updated_at
        }
    except Order.DoesNotExist:
        print(f"Order not found for order_number: {data['order_number']}")
        raise ValueError(f"Order not found for order_number: {data['order_number']}")
    except Exception as e:
        print(f"Failed to update payment status: {e}")
        raise ValueError(f"Failed to update payment status: {e}")
