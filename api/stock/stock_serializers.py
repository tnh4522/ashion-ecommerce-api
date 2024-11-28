from rest_framework import serializers

from api.models import Stock, StockProduct, Product


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['id', 'name', 'description', 'is_active', 'location', 'created_at', 'updated_at']


class StockProductSerializer(serializers.ModelSerializer):
    stock = serializers.PrimaryKeyRelatedField(read_only=False, queryset=Stock.objects.all())
    product = serializers.PrimaryKeyRelatedField(read_only=False, queryset=Product.objects.all())

    class Meta:
        model = StockProduct
        fields = ['id', 'stock', 'product', 'quantity', 'created_at', 'updated_at']