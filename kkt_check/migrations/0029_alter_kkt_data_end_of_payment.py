# Generated by Django 3.2.9 on 2022-01-30 17:03

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('kkt_check', '0028_alter_kkt_data_end_of_payment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kkt',
            name='data_end_of_payment',
            field=models.DateTimeField(default=datetime.datetime(2022, 1, 30, 17, 3, 16, 327061, tzinfo=utc)),
        ),
    ]
