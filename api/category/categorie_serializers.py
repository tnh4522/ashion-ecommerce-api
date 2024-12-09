from rest_framework import serializers
from ..models import Category


class CategorySerializer(serializers.ModelSerializer):
    product_public = serializers.SerializerMethodField()
    subcategory_count = serializers.SerializerMethodField() 
    class Meta:
        model = Category
        fields = (
            'id', 'name', 'parent', 'slug', 'description', 'image',
            'is_active', 'meta_title', 'meta_description', 'sort_order', 'product_public', 'subcategory_count'
        )
    def get_product_public(self, obj):
        return obj.products.count()
    
    def get_subcategory_count(self, obj):
        return obj.subcategories.count()


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

class SubCategorySerializer(serializers.ModelSerializer):
    product_public = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = [
            'id', 
            'name', 
            'slug', 
            'description', 
            'image', 
            'is_active', 
            'meta_title', 
            'meta_description', 
            'sort_order', 
            'parent',
            'product_public'
        ]
    def get_product_public(self, obj):
        return obj.products.count()