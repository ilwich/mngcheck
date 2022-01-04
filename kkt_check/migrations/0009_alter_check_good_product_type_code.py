# Generated by Django 3.2.9 on 2021-12-30 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kkt_check', '0008_alter_check_good_check_kkt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='check_good',
            name='product_type_code',
            field=models.IntegerField(choices=[(1, 'Товар'), (4, 'Услуга'), (10, 'Платеж')], default=1),
        ),
    ]
