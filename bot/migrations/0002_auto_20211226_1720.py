# Generated by Django 3.2.9 on 2021-12-26 14:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bot', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='botuser',
            name='bot_user_status',
            field=models.CharField(default='Авторизация', max_length=64),
        ),
        migrations.AddField(
            model_name='botuser',
            name='login_name',
            field=models.CharField(default=1, max_length=64),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='botuser',
            name='owner',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='auth.user'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='botuser',
            name='user_token',
            field=models.CharField(default=1, max_length=64),
            preserve_default=False,
        ),
    ]
