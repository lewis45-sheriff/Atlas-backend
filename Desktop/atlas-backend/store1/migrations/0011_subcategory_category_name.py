# Generated by Django 5.1.1 on 2024-11-17 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store1', '0010_order_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='subcategory',
            name='category_name',
            field=models.CharField(blank=True, help_text='Manually input the category name if not selecting from the list', max_length=255, null=True),
        ),
    ]
