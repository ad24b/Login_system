# Generated by Django 5.2.1 on 2025-05-29 04:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_profile_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='phone',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
