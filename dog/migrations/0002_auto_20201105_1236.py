# Generated by Django 3.1.2 on 2020-11-05 19:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dog',
            name='kennel',
            field=models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.CASCADE, to='dog.kennel', to_field='name'),
        ),
    ]
