from rest_framework import serializers
from api.models import Product

class ProductRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'sale_price', 'created_at', 'updated_at', 'status']
