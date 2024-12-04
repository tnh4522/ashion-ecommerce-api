from rest_framework import serializers
from ..models import Category, Product, Tag


class ProductSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Product
        fields = [
            'id', 'user', 'name', 'sku', 'barcode', 'brand', 'description',
            'material', 'care_instructions', 'category', 'price',
            'sale_price', 'start_sale_date', 'end_sale_date', 'stock', 'weight',
            'dimensions', 'sizes', 'colors', 'status', 'is_featured',
            'is_new_arrival', 'is_on_sale', 'main_image', 'video_url',
            'meta_title', 'meta_description', 'slug'
        ]
        read_only_fields = ('user', 'slug')

    def create(self, validated_data):
        user = self.context['request'].user
        tags = validated_data.pop('tags', [])
        product = Product.objects.create(user=user, **validated_data)
        product.tags.set(tags)
        return product

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        return instance
