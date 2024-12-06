from rest_framework import serializers
from ..models import Category


class CategorySerializer(serializers.ModelSerializer):
    product_public = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = (
            'id', 'name', 'parent', 'slug', 'description', 'image',
            'is_active', 'meta_title', 'meta_description', 'sort_order', 'product_public'
        )

def get_product_public(self, obj):
        return obj.products.count()

class CategoryActiveUpdateSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.IntegerField(), 
        allow_empty=False
    )
    is_active = serializers.BooleanField()

class CategoryDeleteSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.IntegerField(), 
        allow_empty=False
    )