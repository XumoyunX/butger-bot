# Generated by Django 4.0 on 2022-01-08 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0024_botsettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='userstype',
            name='status',
            field=models.BooleanField(default=False),
        ),
    ]
