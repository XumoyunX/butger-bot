# Generated by Django 4.0 on 2022-01-08 04:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0019_remove_adsmodel_send_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='adsmodel',
            name='active',
            field=models.IntegerField(default=0),
        ),
    ]