# Generated by Django 5.1.1 on 2024-11-20 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store1', '0012_product_alcohol_content_product_brand_product_origin'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subcategory',
            name='category_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
