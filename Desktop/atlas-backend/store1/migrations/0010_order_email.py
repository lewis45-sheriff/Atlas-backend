# Generated by Django 5.1.1 on 2024-11-16 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store1', '0009_subcategory_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='email',
            field=models.CharField(default='Unknown', max_length=155),
        ),
    ]
