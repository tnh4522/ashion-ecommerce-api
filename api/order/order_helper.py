from flask.json import jsonify

from api.models import PaymentMethod
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
