from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token
from kkt_check.models import Kkt
from icecream import ic


def bot_autorisation(bot_user, msg_text):
    """Ввод имени"""
    bot_user.login_name = msg_text.strip()
    bot_user.bot_user_status = 'Пароль'
    bot_user.save()
    return "Введите пароль"

def login_pass(bot_user, msg_text):
    """Ввод пароля"""
    user = authenticate(username=bot_user.login_name, password=msg_text.strip())
    if user is not None:    # Пользователь авторизован
        bot_user.owner = user
        bot_user.bot_user_status = 'Выбор'
        bot_user.save()
        return f"Пользователь авторизован. Токен {bot_user.user_token}.\nВыберете действие:"
    else:   # Пользователь не найден
        bot_user.bot_user_status = 'Авторизация'
        bot_user.save()
        return "Неверное имя или пароль.\nВведите логин: "

def bot_menu(bot_user, msg_text):
    """Вывод меню выбора"""
    if msg_text == 'Отмена': # Отмена
        bot_user.bot_user_status = 'Авторизация'
        bot_user.save()
        return "Спасибо за работу. \n Авторизация. Введите логин:"
    if msg_text == 'Чек прихода': # Чек прихода
        try:
            kkts = Kkt.objects.filter(owner=bot_user.owner)
        except Kkt.DoesNotExist:
            return 'Список касс пуст'
        bot_user.bot_user_status = 'Выбор кассы'
        bot_user.save()
        res = []
        for kkt in kkts:
            res.append(str(kkt))
        return '\n'.join(res)


    return "Печатаем чек"

def bot_check_kkt(bot_user, msg_text):
    """Выбор кассы"""
    if msg_text == 'Отмена':  # Отмена
        bot_user.bot_user_status = 'Авторизация'
        bot_user.save()
        return "Спасибо за работу. \n Авторизация. Введите логин:"

user_command_status = {
    'Авторизация': bot_autorisation,
    'Пароль': login_pass,
    'Выбор': bot_menu,
    'Выбор кассы': bot_check_kkt
}