# Generated by Django 3.2.9 on 2022-01-01 16:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0004_botuser_current_сheck_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='botuser',
            old_name='current_сheck_id',
            new_name='current_сheck',
        ),
    ]
