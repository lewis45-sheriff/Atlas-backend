# Generated by Django 5.1.1 on 2024-11-20 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store1', '0011_subcategory_category_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='alcohol_content',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='brand',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='origin',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
