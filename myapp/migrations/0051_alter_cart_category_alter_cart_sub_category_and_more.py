# Generated by Django 4.0 on 2022-02-24 09:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0050_alter_category_desc_alter_subcategory_desc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.category'),
        ),
        migrations.AlterField(
            model_name='cart',
            name='sub_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.subcategory'),
        ),
        migrations.AlterField(
            model_name='comments',
            name='costumer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.costumers'),
        ),
    ]
