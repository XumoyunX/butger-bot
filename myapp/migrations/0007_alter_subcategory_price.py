# Generated by Django 4.0 on 2022-01-04 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_remove_cart_product_cart_count_cart_sub_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subcategory',
            name='price',
            field=models.IntegerField(),
        ),
    ]
