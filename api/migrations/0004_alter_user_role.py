# Generated by Django 5.1.1 on 2024-10-13 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_remove_product_seller_product_user_permission'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('ADMIN', 'Administrator'), ('MANAGER', 'Manager'), ('STAFF', 'Staff'), ('SELLER', 'Seller'), ('BUYER', 'Buyer')], default='BUYER', max_length=10),
        ),
    ]