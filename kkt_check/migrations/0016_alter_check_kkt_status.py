# Generated by Django 3.2.9 on 2022-01-05 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kkt_check', '0015_alter_check_kkt_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='check_kkt',
            name='status',
            field=models.CharField(default='Добавлен', max_length=100),
        ),
    ]
