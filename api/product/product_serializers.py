# product/product_serializers.py

from rest_framework import serializers
from ..models import Category, Product, Tag, ProductImage, StockVariant, Stock
from .variant_serializers import StockVariantSerializer
from django.db import transaction
from django.db.models import Sum
import logging

logger = logging.getLogger(__name__)

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_main', 'caption', 'alt_text', 'order']

class ProductSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False, allow_null=True)
    images = ProductImageSerializer(source='product_images', many=True, read_only=True)
    stock_variants = StockVariantSerializer(many=True, read_only=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, required=False)

    class Meta:
        model = Product
        fields = [
            'id', 'user', 'name', 'slug', 'sku', 'barcode', 'brand', 'description',
            'material', 'care_instructions', 'category', 'price',
            'sale_price', 'start_sale_date', 'end_sale_date', 'stock', 'weight',
            'dimensions', 'sizes', 'colors', 'status', 'is_featured',
            'is_new_arrival', 'is_on_sale', 'main_image', 'video_url',
            'meta_title', 'meta_description', 'slug', 'images', 'stock_variants', 'tags'
        ]
        read_only_fields = ('user', 'slug', 'stock_variants')

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

        self.sync_stock_variants(product)

        return product

    def get_main_image(self, obj):
        if obj.images.exists():
            request = self.context.get('request')
            image_url = obj.images.first().image.url
            return request.build_absolute_uri(image_url)
        return None

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        replaced_image_ids = self.context['request'].data.getlist('replaced_image_id')
        new_images = self.context['request'].FILES.getlist('images')

        # Lưu trữ Sizes và Colors cũ để so sánh
        original_sizes = set([size.strip().upper() for size in instance.sizes.split(',') if size.strip()])
        original_colors = set([color.strip().upper() for color in instance.colors.split(',') if color.strip()])

        # Cập nhật các trường khác
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if tags is not None:
            instance.tags.set(tags)

        # Xử lý hình ảnh
        for replaced_id, new_image in zip(replaced_image_ids, new_images):
            try:
                product_image = ProductImage.objects.get(id=replaced_id, product=instance)
                product_image.image = new_image
                product_image.save()
            except ProductImage.DoesNotExist:
                continue

        remaining_images = new_images[len(replaced_image_ids):]
        for new_image in remaining_images:
            ProductImage.objects.create(
                product=instance,
                image=new_image,
                is_main=False,
                order=instance.product_images.count()
            )

        # Xử lý Sizes và Colors mới
        new_sizes = set([size.strip().upper() for size in validated_data.get('sizes', '').split(',') if size.strip()])
        new_colors = set([color.strip().upper() for color in validated_data.get('colors', '').split(',') if color.strip()])

        # Kiểm tra sự thay đổi
        sizes_changed = original_sizes != new_sizes
        colors_changed = original_colors != new_colors

        if sizes_changed or colors_changed:
            # Đồng bộ các StockVariant
            self.sync_stock_variants(instance, new_sizes, new_colors)

            # Cập nhật Stock tổng cộng
            self.update_product_stock(instance)

        return instance

    def sync_stock_variants(self, product, new_sizes=None, new_colors=None):

        if new_sizes is None:
            sizes = set([size.strip().upper() for size in product.sizes.split(',') if size.strip()])
        else:
            sizes = new_sizes

        if new_colors is None:
            colors = set([color.strip().upper() for color in product.colors.split(',') if color.strip()])
        else:
            colors = new_colors

        valid_variant_names = set(f"{size} - {color}" for size in sizes for color in colors)
        active_stocks = Stock.objects.filter(is_active=True)

        with transaction.atomic():
            # Tạo các StockVariant mới nếu chưa tồn tại
            for stock in active_stocks:
                for variant_name in valid_variant_names:
                    variant, created = StockVariant.objects.get_or_create(
                        product=product,
                        stock=stock,
                        variant_name=variant_name,
                        defaults={'quantity': 0}
                    )
                    if created:
                        logger.info(f"Created StockVariant: {variant_name} for Product: {product.name} at Stock: {stock.name}")

            # Xóa các StockVariant không hợp lệ
            existing_variants = StockVariant.objects.filter(product=product)
            invalid_variants = existing_variants.exclude(variant_name__in=valid_variant_names)
            count_deleted = invalid_variants.count()
            if count_deleted > 0:
                invalid_variants.delete()
                logger.info(f"Deleted {count_deleted} invalid StockVariants from Product: {product.name}")
            else:
                logger.info(f"No invalid StockVariants found for Product: {product.name}")

    def update_product_stock(self, product):
        total_quantity = StockVariant.objects.filter(product=product).aggregate(total=Sum('quantity'))['total'] or 0
        product.stock = total_quantity
        product.save(update_fields=['stock'])
        logger.info(f"Updated Product Stock: {product.name} - Total Quantity: {total_quantity}")

    def validate(self, attrs):
        sizes = set([size.strip().upper() for size in attrs.get('sizes', '').split(',') if size.strip()])
        colors = set([color.strip().upper() for color in attrs.get('colors', '').split(',') if color.strip()])

        variant_names = [f"{size} - {color}" for size in sizes for color in colors]
        if len(variant_names) != len(set(variant_names)):
            raise serializers.ValidationError("There are duplicate variant names.")

        return attrs
