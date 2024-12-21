from rest_framework import serializers
from api.models import Customer, Order, OrderItem, Product


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            'product', 'quantity', 'price', 'total_price', 'size', 'color', 'weight'
        ]


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'customer', 'order_number', 'subtotal_price', 'shipping_cost',
            'discount_amount', 'tax_amount', 'total_price', 'total_weight',
            'shipping_address', 'billing_address', 'shipping_method',
            'payment_method', 'payment_status', 'status', 'coupon',
            'loyalty_points_used', 'tracking_number', 'estimated_delivery_date',
            'note', 'transaction_id', 'created_at', 'updated_at', 'items'
        ]
        read_only_fields = ('user', 'order_number')

    def create(self, validated_data):
        print(validated_data) # test data
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        order = Order.objects.create(user=user, **validated_data)

        for item_data in items_data:
            product = Product.objects.get(id=item_data['product'].id)
            seller = item_data.get('seller', product.user)
            OrderItem.objects.create(order=order, seller=seller, **item_data)

        return order
    
    def update(self, instance, validated_data):
        if 'items' in validated_data:
            items_data = validated_data.pop('items')
            existing_items = {item.id: item for item in instance.items.all()}
            
            for item_data in items_data:
                product = Product.objects.get(id=item_data['product'].id)
                seller = item_data.get('seller', product.user)

                if 'id' in item_data and item_data['id'] in existing_items:
                    existing_item = existing_items[item_data['id']]
                    for attr, value in item_data.items():
                        setattr(existing_item, attr, value)
                    existing_item.seller = seller
                    existing_item.save()
                else:
                    OrderItem.objects.create(order=instance, seller=seller, **item_data)

            provided_ids = [item_data['id'] for item_data in items_data if 'id' in item_data]
            for item_id, item in existing_items.items():
                if item_id not in provided_ids:
                    item.delete()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class OrderItemSerializerForView(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    product_image = serializers.ImageField(source='product.main_image')
    class Meta:
        model = OrderItem
        fields = [
            'product', 'seller', 'quantity', 'price', 'total_price', 'size', 'color', 'weight', 'product_name', 'product_image'
        ]


class OrderSerializerForView(serializers.ModelSerializer):
    items = OrderItemSerializerForView(many=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'subtotal_price', 'shipping_cost', 'discount_amount',
            'tax_amount', 'total_price', 'total_weight', 'shipping_address',
            'billing_address', 'shipping_method', 'payment_method', 'payment_status',
            'status', 'coupon', 'loyalty_points_used', 'tracking_number',
            'estimated_delivery_date', 'note', 'transaction_id', 'created_at',
            'updated_at', 'items'
        ]
        read_only_fields = fields
