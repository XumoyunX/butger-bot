# Generated by Django 4.0 on 2022-01-07 04:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('myapp', '0010_rename_text_texts'),
    ]

    operations = [
        migrations.CreateModel(
            name='UsersType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('admin', 'Admin'), ('manager', 'Manager'), ('kassir', 'Kassir')], max_length=200)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
        ),
    ]