# Generated by Django 3.1.2 on 2020-10-20 21:53

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('dog', '0002_auto_20201019_2045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dog',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
