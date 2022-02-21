from django.urls import path
from . import views


app_name = 'bot'
urlpatterns = [
    path('hook/', views.talkin_to_me_bruh),
    # Обработка сообщений телеграммбота
    path('msg_command_center/<int:kkt_id>/', views.msg_command_center, name='kkt'),
    # Cтраница авторизации по ссылке из телеграмм бота
    path('telebot_new_user/<int:message_from_id>/', views.telebot_new_user, name='telebot_new_user'),
    # Страница со списком всех операторов телеграмм бота пользователя.
    path('botusers_list/', views.botusers_list, name='botusers_list'),
    # Удаление телеграмм аккаунта сотрудника
    path('del_botuser/<int:bot_id>/', views.del_botuser, name='del_botuser'),
]