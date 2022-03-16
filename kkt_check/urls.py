"""Определяет схемы URL для kkt_check."""

from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.authtoken import views
from . import views

app_name = 'kkt_check'
urlpatterns = [
    # Домашняя страница
    path('', views.index, name='index'),
    # Страница со списком всех ккт.
    path('kktlist/', views.kktlist, name='kktlist'),
    # Страница с подробной информацией по отдельной кассе
    path('kkt/<int:kkt_id>/', views.kkt, name='kkt'),
    # Страница для добавления новой кассы
    path('new_kkt/', views.new_kkt, name='new_kkt'),
    # Страница для редактирования кассы
    path('edit_kkt/<int:kkt_id>/', views.edit_kkt, name='edit_kkt'),
    # Удаление кассы
    path('del_kkt/<int:kkt_id>/', views.del_kkt, name='del_kkt'),
    # Страница для добавления нового чека
    path('new_check_kkt/<int:kkt_id>/', views.new_check_kkt, name='new_check_kkt'),
    # Страница для редактирования чека
    path('edit_check_kkt/<int:check_kkt_id>/', views.edit_check_kkt, name='edit_check_kkt'),
    # Фискализация чека
    path('fisk_check_kkt/<int:check_kkt_id>/', views.fisk_check_kkt, name='fisk_check_kkt'),
    # Удаление чека
    path('del_check_kkt/<int:check_kkt_id>/', views.del_check_kkt, name='del_check_kkt'),
    # Страница для добавления нового товара в чек
    path('new_good_check_kkt/<int:check_kkt_id>/', views.new_good_check_kkt, name='new_good_check_kkt'),
    # Страница для редактирования товара в чеке
    path('edit_good_check_kkt/<int:good_check_kkt_id>/', views.edit_good_check_kkt, name='edit_good_check_kkt'),
    # Удаление товара в чеке
    path('del_good_check_kkt/<int:good_check_kkt_id>/', views.del_good_check_kkt, name='del_good_check_kkt'),
    # API список ККТ
    path('api/kkts/', views.GetKktInfoView.as_view()),
    # API просмотр и изменение ККТ по номеру ФН
    path('api/kkt/<int:fn_number>/', views.GetKktDetail.as_view()),
    # API список чеков по номеру ФН
    path('api/check_kkt/<int:fn_number>', views.GetCheckInfoView.as_view()),
    # API просмотр и изменение чека ККТ по номеру ФН и времени создания чека
    path('api/check_kkt/<int:fn_number>/<str:date_added>', views.GetCheckDetail.as_view()),
    # API получение токена авторизации
    path('api-token-auth/', obtain_auth_token),
    ]