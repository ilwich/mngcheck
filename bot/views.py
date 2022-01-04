from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from bot.models import Botuser, Botmessage
from datetime import datetime
from icecream import ic
import json
from django.views.decorators.csrf import csrf_exempt

from telepot import Bot
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
from bot.botcommand import user_command_status
import os

TOKEN = os.environ.get("BOT_TOKEN")
TelegramBot = Bot(TOKEN)


def send_answer(bot_user, msg, markup_msgs):
    """Отправка сообщения в телеграм пользователю bot model"""
    if markup_msgs != None:
        n = 2  # Разбиваем кнопки на количество столбиков n
        keyboard = [markup_msgs[i:i+n] for i in range(0, len(markup_msgs), n)]
        markup = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
        TelegramBot.sendMessage(bot_user.bot_user_id, msg, reply_markup=markup)
    else:
        TelegramBot.sendMessage(bot_user.bot_user_id, msg)
    return True


def bot_cancel_message(bot_user, msg_text):
    """Проверка ссобщения Отмена от пользователя"""
    if msg_text in ['Отмена', 'отмена', 'выход', 'Выход']:  # Отмена
        bot_user.bot_user_status = 'Авторизация'
        bot_user.save()
        return {"text": "Спасибо за работу. \n Авторизация. Введите логин:",
                "markup": ['Отмена']}
    else:
        return False


def msg_command_center(bot_msg):
    """Обработка нового сообщения от бота.Выполняем функцию по текущему статусу пользователя"""
    res = bot_cancel_message(bot_msg.sender, bot_msg.text)  # Проверка команды Отмена
    if res:
        send_answer(bot_msg.sender, res['text'], res['markup'])
        return True
    else:
        res_answer = user_command_status.get(bot_msg.sender.bot_user_status)(bot_msg.sender, bot_msg.text)
        try:
            send_answer(bot_msg.sender, res_answer['text'], res_answer['markup'])
            return True
        except ValueError:
            return "Message error"


@csrf_exempt
def talkin_to_me_bruh(request):
    """Входной запрос от телеграмм"""

    def _is_user_registered(user_id: int) -> bool:
        """Проверка что пользовательский id в списке bot_uesrs """
        if Botuser.objects.filter(bot_user_id__exact=user_id).count() > 0:
            return True
        return False

    def _update_id_exists(update_id: int) -> bool:
        """Проверка что сообщение уже было принято от пользователя"""
        if Botmessage.objects.filter(update_id__exact=update_id).count() > 0:
            return True
        return False

    def _add_message_to_db(json_dict: dict) -> (None, True):
        """Добавление сообщения в базу сообщений сообщений бота"""
        try:
            sender_id = json_dict['message']['from'].get('id')
            update_id = json_dict.get('update_id')
            sender_is_bot = None if json_dict['message']['from'].get('is_bot') is True else False
            message_text = json_dict['message'].get('text')
            message_date = json_dict['message'].get('date')
        except KeyError:
            return None
        if None in (sender_id, sender_is_bot, update_id, message_text, message_date):
            return None

        if _update_id_exists(update_id):
            return True

        if _is_user_registered(sender_id):  # Проверка что id пользователя в базе
            try:
                new_bot_msg = Botmessage(
                    update_id=int(update_id),
                    text=str(message_text),
                    sender=Botuser.objects.filter(bot_user_id__exact=sender_id).get(),
                    date=datetime.fromtimestamp(int(message_date)),
                )
                new_bot_msg.save()
                msg_command_center(bot_msg=new_bot_msg)
                return True
            except (KeyError, ValueError):
                return None
        else:
            try:
                if str(message_text) == "/start":  # добавление нового пользователя по команде страрт
                    new_bot_user = Botuser(
                        bot_user_id=int(sender_id),
                        first_name=str(json_dict['message']['from'].get('first_name')),
                        last_name=str(json_dict['message']['from'].get('last_name')),

                    )
                    new_bot_user.save()
                    send_answer(new_bot_user, new_bot_user.bot_user_status)
                return True
            except (KeyError, ValueError):
                return None


    # перевод в json
    try:
        json_message = json.loads(request.body)
    except json.decoder.JSONDecodeError as err:
        return HttpResponse(str(err))
    # добавление в базу сообщений
    try:
        result = _add_message_to_db(json_message)
    except ValueError as e:
        return HttpResponseBadRequest(str(e))
    if result is True:
        return HttpResponse('OK')
    else:
        return HttpResponseBadRequest('Malformed or incomplete JSON data received')
