# Generated by Django 5.1.1 on 2024-11-18 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_alter_store_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brand_name', models.CharField(max_length=255)),
                ('brand_description', models.TextField(blank=True)),
                ('brand_logo', models.ImageField(blank=True, null=True, upload_to='brand_logos/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_verified', models.BooleanField(default=False)),
            ],
        ),
    ]
