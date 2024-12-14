from rest_framework import serializers
from ..models import Stock

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['id', 'name', 'description', 'is_active', 'location', 'created_at', 'updated_at']

