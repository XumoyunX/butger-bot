# Generated by Django 4.0 on 2022-01-24 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0045_alter_comments_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='cost_type',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
