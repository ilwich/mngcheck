# Generated by Django 3.2.9 on 2021-11-22 18:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kkt_check', '0006_rename_check_kkt_check_good_checkkkt'),
    ]

    operations = [
        migrations.RenameField(
            model_name='check_good',
            old_name='checkkkt',
            new_name='check_kkt',
        ),
    ]
