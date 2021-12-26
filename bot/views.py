from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from bot.models import Botuser, Botmessage
from datetime import datetime
from icecream import ic
import json
from django.views.decorators.csrf import csrf_exempt

from telepot import Bot
from bot.botcommand import user_command_status
import os

TOKEN = os.environ.get("BOT_TOKEN")
TelegramBot = Bot(TOKEN)



def send_answer(bot_user, msg):
    """Отправка сообщения в телеграм пользователю bot model"""
    TelegramBot.sendMessage(bot_user.bot_user_id, msg)
    return True

def msg_command_center(bot_msg):
    """Обработка нового сообщения от бота"""
    #Выполняем функцию по текущему статусу пользователя
    res_answer = user_command_status.get(bot_msg.sender.bot_user_status)(bot_msg.sender, bot_msg.text)
    send_answer(bot_msg.sender, res_answer)
    return True

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
            sender_object = Botuser.objects.filter(bot_user_id__exact=sender_id).get()
            update_id = json_dict.get('update_id')
            message_text = json_dict['message'].get('text')
            message_date = json_dict['message'].get('date')
        except KeyError:
            return None
        if None in (sender_id, update_id, message_text, message_date):
            return None

        if _update_id_exists(update_id):
            return True

        if _is_user_registered(sender_id):  #Проверка что id пользователя в базе
            try:
                new_bot_msg = Botmessage(
                    update_id=int(update_id),
                    text=str(message_text),
                    sender=sender_object,
                    date=datetime.fromtimestamp(int(message_date)),
                )
                new_bot_msg.save()
                msg_command_center(bot_msg=new_bot_msg)
                return True
            except (KeyError, ValueError):
                return None
        else:
            raise ValueError('Sender is rejected')

    #перевод в json
    try:
        json_message = json.loads(request.body)
    except json.decoder.JSONDecodeError as err:
        return HttpResponse(str(err))
    #добавление в базу сообщений
    try:
        result = _add_message_to_db(json_message)
    except ValueError as e:
        return HttpResponseBadRequest(str(e))
    if result is True:
        return HttpResponse('OK')
    else:
        return HttpResponseBadRequest('Malformed or incomplete JSON data received')
