# Generated by Django 4.0 on 2022-01-07 05:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0012_userstype_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='active',
            field=models.BooleanField(default=False),
        ),
    ]
