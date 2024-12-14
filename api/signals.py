
import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product, StockVariant, Stock
from django.db.models import Sum
from django.db import transaction

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Product)
def sync_stock_variants(sender, instance, created, **kwargs):
    """
    Synchronize StockVariants with the current sizes and colors of the Product.
    - Create missing StockVariants for valid size-color combinations in each active stock.
    - Delete StockVariants that are no longer valid.
    """
    logger.info(f"Synchronizing StockVariants for Product: {instance.name} (Created: {created})")

    sizes = set([size.strip().upper() for size in instance.sizes.split(',') if size.strip()])
    colors = set([color.strip().upper() for color in instance.colors.split(',') if color.strip()])

    valid_variant_names = set(f"{size} - {color}" for size in sizes for color in colors)

    active_stocks = Stock.objects.filter(is_active=True)

    for stock in active_stocks:
        for variant_name in valid_variant_names:
            if not StockVariant.objects.filter(product=instance, stock=stock, variant_name=variant_name).exists():
                with transaction.atomic():
                    StockVariant.objects.create(
                        product=instance,
                        stock=stock,
                        variant_name=variant_name,
                        quantity=0
                    )
                logger.info(f"Created StockVariant: {variant_name} for Product: {instance.name} at Stock: {stock.name}")

    # Xóa StockVariants không hợp lệ
    existing_variants = StockVariant.objects.filter(product=instance)
    invalid_variants = existing_variants.exclude(variant_name__in=valid_variant_names)
    count_deleted = invalid_variants.count()
    if count_deleted > 0:
        invalid_variants.delete()
        logger.info(f"Deleted {count_deleted} invalid StockVariants from Product: {instance.name}")
    else:
        logger.info(f"No invalid StockVariants found for Product: {instance.name}")


def update_product_stock(product):
    """
    Update the total stock of the Product based on its StockVariants.
    """
    total_quantity = StockVariant.objects.filter(product=product).aggregate(total=Sum('quantity'))['total'] or 0
    product.stock = total_quantity
    product.save(update_fields=['stock'])
    logger.info(f"Updated Product Stock: {product.name} - Total Quantity: {total_quantity}")


@receiver(post_save, sender=StockVariant)
def update_product_stock_on_variant_save(sender, instance, **kwargs):
    """
    Update the Product's total stock when a StockVariant is saved.
    """
    logger.info(f"StockVariant saved: {instance.variant_name}, quantity: {instance.quantity}")
    update_product_stock(instance.product)


@receiver(post_delete, sender=StockVariant)
def update_product_stock_on_variant_delete(sender, instance, **kwargs):
    """
    Update the Product's total stock when a StockVariant is deleted.
    """
    logger.info(f"StockVariant deleted: {instance.variant_name}")
    update_product_stock(instance.product)

