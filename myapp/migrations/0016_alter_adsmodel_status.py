# Generated by Django 4.0 on 2022-01-07 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0015_adsmodel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adsmodel',
            name='status',
            field=models.CharField(choices=[('0', 'Barcha'), ('1', 'Uz'), ('2', 'Ru')], max_length=100),
        ),
    ]