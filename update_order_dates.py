from django.utils import timezone
from api.models import Order
import datetime

orders = Order.objects.all()

day = 1  
for order in orders:
    new_date = timezone.datetime(
        year=timezone.now().year,
        month=12,
        day=day,
        hour=0,
        minute=0,
        second=0,
        tzinfo=datetime.timezone.utc  
    )
    order.created_at = new_date
    order.save()
    print(f"Order {order.order_number} - New created_at: {order.created_at}")

    day += 1

    if day > 31:
        day = 1
