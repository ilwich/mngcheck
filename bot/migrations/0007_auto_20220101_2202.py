# Generated by Django 3.2.9 on 2022-01-01 19:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kkt_check', '0011_alter_check_good_qty'),
        ('bot', '0006_botuser_current_goods'),
    ]

    operations = [
        migrations.AlterField(
            model_name='botuser',
            name='current_goods',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='kkt_check.check_good'),
        ),
        migrations.AlterField(
            model_name='botuser',
            name='current_сheck',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='kkt_check.check_kkt'),
        ),
    ]
