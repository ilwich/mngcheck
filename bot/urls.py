from django.urls import path
from . import views


app_name = 'bot'
urlpatterns = [
    path('hook/', views.talkin_to_me_bruh),
    # Обработка сообщений телеграммбота
    path('msg_command_center/<int:kkt_id>/', views.msg_command_center, name='kkt'),
]