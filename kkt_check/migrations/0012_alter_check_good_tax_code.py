# Generated by Django 3.2.9 on 2022-01-02 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kkt_check', '0011_alter_check_good_qty'),
    ]

    operations = [
        migrations.AlterField(
            model_name='check_good',
            name='tax_code',
            field=models.IntegerField(choices=[(6, 'Ндс Не Облагается'), (1, 'Ставка Ндс 20'), (2, 'Ставка Ндс 10'), (5, 'Ставка Ндс 0')], default=6),
        ),
    ]
