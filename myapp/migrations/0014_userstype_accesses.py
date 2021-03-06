# Generated by Django 4.0 on 2022-01-07 10:39

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0013_address_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='userstype',
            name='accesses',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('order', 'Zakaz'), ('menu', 'Menu'), ('statistic', 'Statistika'), ('Ad', 'Ad'), ('fillial', 'Fillial'), ('users', 'Users'), ('followers', 'Followers'), ('settings_bot', 'Bot Settings'), ('settings_bot', 'Bot Settings')], default='', max_length=73),
            preserve_default=False,
        ),
    ]
