# Generated by Django 4.0 on 2022-01-18 09:54

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0040_botsettings_click_botsettings_payme'),
    ]

    operations = [
        migrations.AddField(
            model_name='subcategory',
            name='desc',
            field=ckeditor.fields.RichTextField(default=''),
            preserve_default=False,
        ),
    ]
