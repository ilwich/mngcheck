# Generated by Django 3.2.9 on 2022-01-31 17:17

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('partners', '0009_auto_20220131_0013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='date_added',
            field=models.DateTimeField(default=datetime.datetime(2022, 1, 31, 17, 17, 45, 3574, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='contract',
            name='date_end_payment',
            field=models.DateTimeField(default=datetime.datetime(2022, 1, 31, 17, 17, 45, 3574, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='paymentcode',
            name='date_added',
            field=models.DateTimeField(default=datetime.datetime(2022, 1, 31, 17, 17, 45, 3574, tzinfo=utc)),
        ),
        migrations.CreateModel(
            name='CodeOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code_count', models.CharField(default=1, max_length=6)),
                ('date_added', models.DateTimeField(default=datetime.datetime(2022, 1, 31, 17, 17, 45, 3574, tzinfo=utc))),
                ('payment_status', models.CharField(default='Создан', max_length=30)),
                ('mounth_payment_count', models.IntegerField(default=12)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
