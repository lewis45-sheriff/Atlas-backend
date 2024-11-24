# Generated by Django 5.1.1 on 2024-11-20 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store1', '0013_alter_subcategory_category_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subcategory',
            name='category',
        ),
        migrations.AddField(
            model_name='order',
            name='Country',
            field=models.CharField(default='Unknown', max_length=100),
        ),
        migrations.AddField(
            model_name='order',
            name='location',
            field=models.CharField(default='Unknown', max_length=100),
        ),
        migrations.AlterField(
            model_name='order',
            name='email',
            field=models.CharField(default='Unknown', max_length=100),
        ),
        migrations.AlterField(
            model_name='order',
            name='phone_number',
            field=models.CharField(default='Unknown', max_length=15),
        ),
    ]
