import requests
from django.core.cache import cache
from api.models import ModulePayment, Customer


def get_access_token():
    try:
        MODULE_NAME = 'vivapayments'
        config = ModulePayment.objects.get(module_name=MODULE_NAME)

        is_test_mode = config.test_mode.lower() == 'on'
        client_id = config.client_id_test if is_test_mode else config.client_id_prod
        client_secret = config.client_secret_test if is_test_mode else config.client_secret_prod
        connect_token_url = config.connect_token_url_test if is_test_mode else config.connect_token_url_prod

        if not client_id or not client_secret or not connect_token_url:
            raise ValueError("Missing necessary configuration for access token retrieval.")

        # Check if the token is cached
        access_token = cache.get('viva_access_token')
        if access_token:
            return access_token

        # Request new access token
        response = requests.post(
            connect_token_url,
            data={
                'client_id': client_id,
                'client_secret': client_secret,
                'grant_type': 'client_credentials'
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        response.raise_for_status()
        data = response.json()

        if 'access_token' not in data:
            raise ValueError("Error Processing Request: No Access Token")

        # Cache the token with expiration
        expires_in = data.get('expires_in', 3600)
        cache.set('viva_access_token', data['access_token'], timeout=expires_in)

        return data['access_token']
    except Exception as e:
        print(f"Failed to get access token: {e}")
        raise


def handle_data_before_payment(request_data, order_data):
    try:
        total_amount = int(float(request_data['total_price']) * 100)

        customer_id = request_data['customer']
        customer_obj = Customer.objects.get(id=customer_id)

        customer = {
            "email": customer_obj.email or f"customer{customer_id}@example.com",
            "fullName": f"{customer_obj.first_name} {customer_obj.last_name}".strip(),
            "phone": customer_obj.phone_number or "+1234567890",
            "countryCode": "US",
            "requestLang": "en-US"
        }

        merchant_trns = order_data['order_number']

        source_code = "4715"

        payment_details = {
            "amount": total_amount,
            "customer": customer,
            "sourceCode": source_code,
            "merchantTrns": merchant_trns
        }

        return payment_details
    except Customer.DoesNotExist:
        raise ValueError(f"Customer with ID {customer_id} does not exist.")
    except KeyError as e:
        print(f"Missing key in request data: {e}")
        raise ValueError(f"Missing key: {e}")
    except Exception as e:
        print(f"Error in handle_data_before_payment: {e}")
        raise


def process_payment(request_data, order_data):
    try:
        MODULE_NAME = 'vivapayments'
        config = ModulePayment.objects.get(module_name=MODULE_NAME)
        data = handle_data_before_payment(request_data, order_data)

        is_test_mode = config.test_mode.lower() == 'on'
        base_url = config.base_url_test if is_test_mode else config.base_url_prod
        merchant_id = config.merchant_id_test if is_test_mode else config.merchant_id_prod

        if not base_url or not merchant_id:
            raise ValueError("Missing necessary configuration for processing payment.")

        endpoint = f"{base_url}/checkout/v2/orders?merchantId={merchant_id}"

        access_token = get_access_token()

        response = requests.post(
            endpoint,
            json=data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
        )
        response.raise_for_status()

        return response.json()
    except Exception as e:
        print(f"Failed to process payment: {e}")
        raise
