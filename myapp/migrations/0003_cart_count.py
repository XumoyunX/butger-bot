# Generated by Django 4.0 on 2021-12-27 06:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='count',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
