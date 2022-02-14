"""Определяет схемы URL для партнеров"""
from django.urls import path, include
from . import views

app_name = 'partners'
urlpatterns = [
    # Список контрактов партнера
    path('contracts/', views.contracts, name='contracts'),
    # Добавление контракта
    path('new_contract/', views.new_contract, name='new_contract'),
    # Просмотр контракта
    path('view_contract/<int:contract_id>/', views.view_contract, name='view_contract'),
    # Удаление контракта
    path('del_contract/<int:contract_id>/', views.del_contract, name='del_contract'),
    # Оплата тарифа по контракту
    path('payment_contract/<int:contract_id>/', views.payment_contract, name='payment_contract'),
    # Список поиска контрактов партнера
    path('contracts/seach_contract', views.seach_contract, name='seach_contract'),
    # Просмотр кодов активации
    path('view_payment_codes/', views.view_payment_codes, name='view_payment_codes'),
    # Просмотр кодов активации
    path('make_oder/', views.make_oder, name='make_oder'),
    # Список партнеров дилера
    path('partners/', views.partners, name='partners'),
    # Список заказов партнера
    path('view_order/<int:partner_id>/', views.view_order, name='view_order'),
    # Удаление заказа диллером
    path('del_order/<int:order_id>/', views.del_order, name='del_order'),
    # Отправка кодов по заказу партнера
    path('order_send/<int:order_id>/', views.order_send, name='order_send'),
        ]