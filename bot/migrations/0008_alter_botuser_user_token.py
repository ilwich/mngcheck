# Generated by Django 3.2.9 on 2022-01-04 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0007_auto_20220101_2202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='botuser',
            name='user_token',
            field=models.CharField(default='1', max_length=64),
        ),
    ]
