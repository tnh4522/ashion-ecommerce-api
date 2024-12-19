from rest_framework import serializers
from ..models import StockVariant, Stock
from .stock_serializers import StockSerializer


class StockVariantSerializer(serializers.ModelSerializer):
    stock = StockSerializer(read_only=True)
    stock_id = serializers.PrimaryKeyRelatedField(
        queryset=Stock.objects.all(), source='stock', write_only=True
    )
    quantity = serializers.IntegerField()

    class Meta:
        model = StockVariant
        fields = ['id', 'product', 'stock', 'variant_name', 'quantity', 'created_at', 'updated_at', 'stock_id', 'image']
        read_only_fields = ['id', 'product', 'variant_name', 'created_at', 'updated_at']

    def update(self, instance, validated_data):
        instance.quantity = validated_data.get('quantity', instance.quantity)
        if 'stock' in validated_data:
            instance.stock = validated_data['stock']
        if 'image' in validated_data:
            instance.image = validated_data['image']
        instance.save()
        return instance

class StockVariantUpdateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=0)

    def validate_id(self, value):
        if not StockVariant.objects.filter(id=value).exists():
            raise serializers.ValidationError("StockVariant with this ID does not exist.")
        return value

    def update(self, instance, validated_data):
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.save()
        return instance
