# Generated by Django 4.0 on 2022-01-09 07:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0028_remove_order_products_order_comment_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='cart',
            new_name='carts',
        ),
    ]