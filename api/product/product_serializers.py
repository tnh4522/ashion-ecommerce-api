from rest_framework import serializers
from ..models import Category, Product, Tag, ProductImage

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_main', 'caption', 'alt_text', 'order']

class ProductSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False, allow_null=True)
    images = ProductImageSerializer(source='product_images', many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'user', 'name', 'slug', 'sku', 'barcode', 'brand', 'description',
            'material', 'care_instructions', 'category', 'price',
            'sale_price', 'start_sale_date', 'end_sale_date', 'stock', 'weight',
            'dimensions', 'sizes', 'colors', 'status', 'is_featured',
            'is_new_arrival', 'is_on_sale', 'main_image', 'video_url',
            'meta_title', 'meta_description', 'slug', 'images'
        ]
        read_only_fields = ('user', 'slug')

    def create(self, validated_data):
        user = self.context['request'].user
        tags = validated_data.pop('tags', [])
        images = self.context['request'].FILES.getlist('images')
        product = Product.objects.create(user=user, **validated_data)
        product.tags.set(tags)

        for index, image in enumerate(images):
            ProductImage.objects.create(
                product=product,
                image=image,
                is_main=(index == 0),  # First image as main
                order=index
            )

        return product

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        replaced_image_ids = self.context['request'].data.getlist('replaced_image_id')
        new_images = self.context['request'].FILES.getlist('images')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if tags is not None:
            instance.tags.set(tags)

        # Handle image replacements
        for replaced_id, new_image in zip(replaced_image_ids, new_images):
            try:
                product_image = ProductImage.objects.get(id=replaced_id, product=instance)
                product_image.image = new_image
                product_image.save()
            except ProductImage.DoesNotExist:
                continue  # Or handle the error as needed

        # Handle new images (without replaced_image_id)
        remaining_images = new_images[len(replaced_image_ids):]
        for new_image in remaining_images:
            ProductImage.objects.create(
                product=instance,
                image=new_image,
                is_main=False,
                order=instance.product_images.count()
            )

        return instance
