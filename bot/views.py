from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.shortcuts import redirect, render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from bot.models import Botuser, Botmessage
from users.models import Profile
from datetime import datetime
from icecream import ic
import json
import qrcode
from PIL import Image, ImageDraw, ImageFont
from django.views.decorators.csrf import csrf_exempt
from telepot import Bot
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
from bot.botcommand import user_command_status
import os

TOKEN = os.environ.get("BOT_TOKEN")
TelegramBot = Bot(TOKEN)


def send_qr_check_telebot(kkt_check, reply_to_update_id):
    """Отправка файла картинки с QR в ответ на сообщение"""
    try:
        bot_msg = Botmessage.objects.get(update_id=reply_to_update_id)
    except Botmessage.DoesNotExist:
        return False
    # шрифт лежит в папке статик
    filename = "shtrixfr57.ttf"
    full_path_to_font_file = os.path.join(settings.STATICFILES_DIRS[0], filename)
    # Формируем фон чека от количества строк в текстовом представлении данных чека
    text_check = kkt_check.get_text_of_check()
    image_txt = Image.new("RGB", (450, (text_check.count('\n') + 1) * 21 + 470), "white")
    draw = ImageDraw.Draw(image_txt)
    color = 'Black'
    font = ImageFont.truetype(full_path_to_font_file, size=18, encoding='UTF-8')
    draw.text((10, 10), text_check, font=font, fill=color)
    # формируем qr код чека в картинку
    data_qr = kkt_check.status
    img_qr = qrcode.make(data_qr)
    # вставляем картинку qr на картинку чека
    image_txt.paste(img_qr, (0, (text_check.count('\n') + 1) * 21 + 20))
    filename = f"qr_check{data_qr[2:15]}.png"
    full_path_to_qr_file = os.path.join(settings.STATICFILES_DIRS[0], filename)
    # Сохраняем результирующий файл
    image_txt.save(full_path_to_qr_file)
    try:
        # Пытаемся отправить файл в ответ на сообщение сформировавшее чек и удаляем файл
        TelegramBot.sendPhoto(bot_msg.sender.bot_user_id, open(full_path_to_qr_file, 'rb'))
        os.remove(full_path_to_qr_file)
    except IOError:
        return False


def send_qr_payment_telebot(data, bot_user):
    """Отправка файла картинки с QR пользователю бота"""
    filename = f"qr_payment{bot_user.bot_user_id}.png"
    full_path_to_qr_file = os.path.join(settings.STATICFILES_DIRS[0], filename)
    # генерируем qr-код
    img = qrcode.make(data)
    # сохраняем img в файл
    img.save(full_path_to_qr_file)
    try:
        TelegramBot.sendPhoto(bot_user.bot_user_id, open(full_path_to_qr_file, 'rb'))
        os.remove(full_path_to_qr_file)
    except IOError:
        return False


@login_required
def telebot_new_user(request, message_from_id):
    """Привязка id телеграм пользователя к пользователю сайта"""
    if Botuser.objects.filter(bot_user_id__exact=message_from_id).count() > 0:
        new_bot_user = Botuser.objects.filter(bot_user_id__exact=message_from_id).get()
        new_bot_user.owner = request.user
        new_bot_user.login_name = request.user.username
        new_bot_user.bot_user_status = 'Проверка регистрации'
        new_bot_user.save()
    return redirect('kkt_check:kktlist')


def send_reply_telebot(msg, reply_to_update_id):
    """Определение сообщения отправки ответа по botmessage_id"""
    try:
        bot_msg = Botmessage.objects.get(update_id=reply_to_update_id)
    except Botmessage.DoesNotExist:
        return False
    markup_msgs = None
    send_answer(bot_msg.sender, '\n'.join([msg, bot_msg.text]), markup_msgs)


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
    if msg_text.lower() in ['отмена', 'выход']:  # Отмена
        bot_user.bot_user_status = 'Авторизация'
        bot_user.save()
        return {"text": "Спасибо за работу. \n Для начала работы нажмите Войти",
                "markup": ['Войти']}
    else:
        return False


def bot_finish_message(bot_msg):
    """Проверка ссобщения Регистрация чека"""
    if bot_msg.text.strip().lower() in ['регистрация чека']:  # Завершение создания чека
        bot_msg.text = bot_msg.sender.current_сheck.get_text_of_check()
        # Информацию чека сохраняем в текст сообщения
        bot_msg.save()
        bot_msg.sender.bot_user_status = 'Выбор'
        bot_msg.sender.save()
        # Сохраняем id сообщения в чек
        bot_msg.sender.current_сheck.bot_message_id = f'telegram msg_id: {str(bot_msg.update_id)}'
        bot_msg.sender.current_сheck.status = 'Добавлен'
        bot_msg.sender.current_сheck.save()
        return {"text": "Пользователь авторизован.\nВыберете действие:",
                "markup": ['Чек прихода', 'Отмена']}
    else:
        return False


def bot_qr_payment_message(bot_msg):
    """Проверка ссобщения QR-код квитанции"""
    if bot_msg.text.strip().lower() in ['qr-код квитанции']:  # Проверка запроса кода квитанции
        # Получаем состав кода из профиля пользователя на основании владельца бота
        bot_msg_user_profile = Profile.objects.filter(user=bot_msg.sender.owner).get()
        # получаем сумму чека для добавления в квитанцию
        summ_of_check = bot_msg.sender.current_сheck._get_goods_summ()
        # получаем ИНН пользователя
        payee_inn = bot_msg.sender.current_сheck.kkt.inn_kkt
        bot_msg.text = bot_msg_user_profile.get_qr_payment_data()+f'|Sum={summ_of_check}|PayeeINN={payee_inn}'
        # Отправляем данные на генерацию QR  и на отправку в бот
        if send_qr_payment_telebot(bot_msg.text, bot_msg.sender):
            # Информацию qr квитанции сохраняем в текст сообщения
            bot_msg.save()
        return {"text": "Квитанция для оплаты сформирована. Продолжите регистрацию чека",
                "markup": None}
    else:
        return False


def msg_command_center(bot_msg):
    """Обработка нового сообщения от бота.Выполняем функцию по текущему статусу пользователя"""
    cancel_message = bot_cancel_message(bot_msg.sender, bot_msg.text)  # Проверка команды Отмена
    finish_message = bot_finish_message(bot_msg)  # Проверка сообщения Регистрировать чек
    QR_payment_message = bot_qr_payment_message(bot_msg)  # Проверка сообщения запрос квитанции
    if cancel_message:
        send_answer(bot_msg.sender, cancel_message['text'], cancel_message['markup'])
        return True
    elif finish_message:
        send_answer(bot_msg.sender, finish_message['text'], finish_message['markup'])
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
                if str(message_text) == "/start":  # добавление нового пользователя по команде старт
                    new_bot_user = Botuser(
                        bot_user_id=int(sender_id),
                        first_name=str(json_dict['message']['from'].get('first_name')),
                        last_name=str(json_dict['message']['from'].get('last_name')),

                    )
                    new_bot_user.save()

                    send_answer(new_bot_user, 'Нажмите кнопку "Войти', ['Войти'])
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


@login_required
def botusers_list(request):
    """Выводит список всех телеграмм сотрудников пользователя."""
    botuserslist = Botuser.objects.filter(owner=request.user).order_by('bot_user_id')
    context = {'botuserslist': botuserslist}
    return render(request, 'bot/botusers.html', context)


@login_required
def del_botuser(request, bot_id):
    """Удаление существующей записи телеграмм аккаунта сотрудника."""
    try:
        botuser = Botuser.objects.get(bot_user_id=bot_id)
    except Botuser.DoesNotExist:
        raise Http404
    if botuser.owner != request.user:
        raise Http404
    botuser.delete()
    return redirect('bot:botusers_list')
