# Generated by Django 5.1.1 on 2025-01-03 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_remove_customer_order_customer_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shipping_address_text',
            field=models.TextField(blank=True),
        ),
    ]
