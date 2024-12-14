# api/management/commands/sync_stock_variants.py

from django.core.management.base import BaseCommand
from api.models import Product, StockVariant, Stock
from django.db import transaction

class Command(BaseCommand):
    help = 'Synchronize StockVariants with the current sizes and colors of Products. It will create missing variants and delete invalid ones.'

    def handle(self, *args, **kwargs):
        products = Product.objects.all()
        active_stocks = Stock.objects.filter(is_active=True)

        for product in products:
            sizes = set([size.strip().upper() for size in product.sizes.split(',') if size.strip()])
            colors = set([color.strip().upper() for color in product.colors.split(',') if color.strip()])
            valid_variant_names = set(f"{size} - {color}" for size in sizes for color in colors)

            for stock in active_stocks:
                for variant_name in valid_variant_names:
                    with transaction.atomic():
                        variant, created = StockVariant.objects.get_or_create(
                            product=product,
                            stock=stock,
                            variant_name=variant_name,
                            defaults={'quantity': 0}
                        )
                        if created:
                            self.stdout.write(self.style.SUCCESS(
                                f"Đã tạo StockVariant: {variant_name} cho Sản phẩm: {product.name} tại Kho: {stock.name}"))

            existing_variants = StockVariant.objects.filter(product=product)
            invalid_variants = existing_variants.exclude(variant_name__in=valid_variant_names)
            count_deleted = invalid_variants.count()
            if count_deleted > 0:
                invalid_variants.delete()
                self.stdout.write(self.style.SUCCESS(
                    f"Đã xóa {count_deleted} StockVariants không hợp lệ từ Sản phẩm: {product.name}"))
            else:
                self.stdout.write(
                    self.style.NOTICE(f"Không tìm thấy StockVariants không hợp lệ cho Sản phẩm: {product.name}"))

        self.stdout.write(self.style.SUCCESS("Đồng bộ StockVariants hoàn tất thành công."))
