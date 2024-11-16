# Generated by Django 5.1.1 on 2024-11-16 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store1', '0006_remove_product_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='first_name',
            field=models.CharField(default='Unknown', max_length=100),
        ),
        migrations.AddField(
            model_name='order',
            name='last_name',
            field=models.CharField(default='Unknown', max_length=100),
        ),
        migrations.AddField(
            model_name='order',
            name='phone_number',
            field=models.CharField(default='Uknown', max_length=15),
        ),
        migrations.AddField(
            model_name='order',
            name='street_address',
            field=models.CharField(default='Unknown', max_length=255),
        ),
    ]