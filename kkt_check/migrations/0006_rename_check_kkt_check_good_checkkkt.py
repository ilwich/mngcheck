# Generated by Django 3.2.9 on 2021-11-22 17:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kkt_check', '0005_auto_20211122_1908'),
    ]

    operations = [
        migrations.RenameField(
            model_name='check_good',
            old_name='check_kkt',
            new_name='checkkkt',
        ),
    ]
