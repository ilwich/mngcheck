"""Определяет схемы URL для пользователей"""
from django.urls import path, include
from . import views

app_name = 'users'
urlpatterns = [
    # Включить URL авторизации по умолчанию.
    path('', include('django.contrib.auth.urls')),
    # Страница регистрации.
    path('register/', views.register, name='register'),
    # Редактирование профиля
    path('edit/', views.edit, name='edit'),
    # Инструкция клиента
    path('clientinstruction/', views.clientinstruction, name='clientinstruction'),
    # Инструкция партнёра
    path('partnerinstruction/', views.partnerinstruction, name='partnerinstruction'),
        ]
