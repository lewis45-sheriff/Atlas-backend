# Generated by Django 5.1.6 on 2025-02-09 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store1', '0006_alter_order_order_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='products'),
        ),
    ]
