# Generated by Django 5.1.1 on 2024-11-23 17:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store1', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='discount',
        ),
        migrations.RemoveField(
            model_name='order',
            name='shipping_fee',
        ),
    ]