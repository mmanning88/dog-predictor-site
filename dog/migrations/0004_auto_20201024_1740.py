# Generated by Django 3.1.2 on 2020-10-24 23:40

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dog', '0003_auto_20201020_1553'),
    ]

    operations = [
        migrations.AddField(
            model_name='dog',
            name='true_outcome',
            field=models.CharField(blank=True, choices=[('Adoption', 'Adoption'), ('Return to Owner', 'Return to Owner'), ('Transfer', 'Transfer'), ('Euthanasia', 'Euthanasia')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='dog',
            name='age',
            field=models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(20)]),
        ),
        migrations.AlterField(
            model_name='dog',
            name='bully',
            field=models.BooleanField(default=False, verbose_name='is this a bully breed?'),
        ),
        migrations.AlterField(
            model_name='dog',
            name='condition',
            field=models.CharField(choices=[('Normal', 'Normal'), ('Injured', 'Injured'), ('sick', 'Sick'), ('Nursing', 'Nursing'), ('Aggressive', 'Aggressive'), ('Aged', 'Aged'), ('Pregnant', 'Pregnant')], default='normal', max_length=40, verbose_name='intake condition'),
        ),
        migrations.AlterField(
            model_name='dog',
            name='primary_color',
            field=models.CharField(choices=[('none', 'None'), ('black', 'Black'), ('brown', 'Brown'), ('white', 'White'), ('blue ', 'Blue'), ('red ', 'Red'), ('tan', 'Tan'), ('yellow', 'Yellow'), ('cream', 'Red'), ('gray', 'Gray'), ('orange', 'Orange'), ('buff', 'Buff'), ('gold', 'Gold'), ('silver', 'Silver')], default='none', max_length=32),
        ),
    ]
