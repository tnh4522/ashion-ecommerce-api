from rest_framework import serializers
from ..models import Cart, CartItem, Product


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    image = serializers.SerializerMethodField()
    price = serializers.ReadOnlyField(source='product.price')

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'quantity', 'size', 'color', 'added_at', 'image', 'price']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.product.main_image and hasattr(obj.product.main_image, 'url'):
            return request.build_absolute_uri(obj.product.main_image.url)
        return None


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'updated_at', 'items']
        read_only_fields = ['user', 'updated_at']


class CartItemSaveSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1)
    size = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    color = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    def validate_product(self, value):
        if not value:
            raise serializers.ValidationError("Product is required.")
        return value
