# Generated by Django 5.1.1 on 2024-11-03 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_role_alter_userpermission_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='permission',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
