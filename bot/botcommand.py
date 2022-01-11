from django.contrib.auth import authenticate, login
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authtoken.models import Token
from kkt_check.models import Kkt, Check_good, Check_kkt
from icecream import ic
from re import findall, compile, fullmatch




def fn_number_in_msg(str_in):
    """Выделим номер ФН в тексте сообщений"""
    for words in str_in.split():
        fn_number = ''.join(i for i in words if i.isdigit())
        if len(fn_number) == 16: return fn_number
    return False


def summ_in_msg(str_in):
    """Выдели сумму в копейках из сообщении"""
    pattern = '(\d*\s*\d*\s*\d+\s*[,.]*\s*\d*)'
    res = findall(pattern, str_in)
    if res:
        res[0] = res[0].replace(',', '.')
        try:
            res_float = float(res[0].replace(' ', ''))
        except:
            res_float = 0.0
        try:
            res_int = int(res_float * 100)
        except:
            res_int = 0
        return res_int
    else:
        return False


def qty_in_msg(str_in):
    """Выделить количество из сообщения в виде  х 10000"""
    pattern = '(\d*\s*\d*\s*\d+\s*[,.]*\s*\d*)'
    res = findall(pattern, str_in)
    if res:
        res[0] = res[0].replace(',', '.')
        try:
            res_float = float(res[0].replace(' ', ''))
        except:
            res_float = 1.0
        try:
            res_int = int(res_float * 10000)
        except:
            res_int = 1
        return res_int
    else:
        return False


def inn_in_msg(str_in):
    """Выделить инн (10 или 12 цифр подряд) из сообщения"""
    pattern = '(\d{12}|\d{10})'
    res = findall(pattern, str_in)
    if res:
        return res[0]
    else:
        return None

def name_and_inn_in_msg(str_in):
    list_of_str_in = str_in.strip().split()
    name_list = []
    res_inn = '0000000000'
    for word_in in list_of_str_in:
        word_inn = inn_in_msg(word_in)
        if word_in.lower() != 'инн' and word_inn is None:
            name_list.append(word_in)
        elif word_inn is not None:
            res_inn = word_inn
    return {'inn': res_inn, 'name': ' '.join(name_list)}


def email_in_msg(str_in):
    """Выделяем email формата example@site.ru из сообщения"""
    regex_mail = compile(r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])")
    if fullmatch(regex_mail, str_in):
        return True
    else:
        return False


def bot_autorisation(bot_user, msg_text):
    """Отправка сообщения со ссылкой на регистрацию нового пользователя телеграмм бота на сайте"""
    bot_user_reg_url = f"{settings.DEFAULT_DOMAIN}/bot/telebot_new_user/{bot_user.bot_user_id}/"
    bot_user.bot_user_status = 'Проверка регистрации'
    bot_user.save()
    return {"text": f"Пройдите регистрацию нового пользователя телеграмм бота по ссылке.\n {bot_user_reg_url}",
            "markup": ['Войти']}


def check_bot_autorisation(bot_user, msg_text):
    """Отправка сообщения соссылкой на регистрацию нового пользователя телеграмм бота на сайте"""
    if msg_text.lower() == 'войти' and bot_user.owner != 3:
        bot_user.bot_user_status = 'Выбор'
        bot_user.save()
        return {"text": "Пользователь авторизован.\nВыберете действие:",
                "markup": ['Чек прихода', 'Отмена']}
    bot_user_reg_url = f"{settings.DEFAULT_DOMAIN}/bot/telebot_new_user/{bot_user.bot_user_id}/"
    return {"text": f"Пройдите регистрацию нового пользователя телеграмм бота по ссылке {bot_user_reg_url}",
            "markup": ['Войти']}


def login_pass(bot_user, msg_text):
    """Ввод пароля"""
    user = authenticate(username=bot_user.login_name, password=msg_text.strip())
    if user is not None:    # Пользователь авторизован
        bot_user.owner = user
        bot_user.bot_user_status = 'Выбор'
        bot_user.save()
        return {"text": "Пользователь авторизован.\nВыберете действие:",
                "markup": ['Чек прихода', 'Отмена']}
    else:   # Пользователь не найден
        bot_user.bot_user_status = 'Авторизация'
        bot_user.save()
        return {"text": "Неверное имя или пароль.\nВведите логин: ",
                "markup": ['Отмена']}


def bot_menu(bot_user, msg_text):
    """Вывод меню выбора"""
    if msg_text == 'Чек прихода': # Чек прихода
        kkts = Kkt.objects.filter(owner=bot_user.owner)
        if kkts.count() == 0:
            return {"text": "Список касс пуст. Необходимо добавить кассу на сайте",
                    "markup": ['Чек прихода', 'Отмена']}
        else:
            bot_user.bot_user_status = 'Выбор кассы'
            bot_user.save()
            res = []
            for kkt in kkts:
                res.append(str(kkt))
            res.append('Отмена')
            return {"text": "Выбирайте кассу",
                    "markup": res}
    return {"text": "Выбирайте действие",
            "markup": None}


def bot_check_kkt(bot_user, msg_text):
    """Выбор кассы"""
    if fn_number_in_msg(msg_text):
        kkts = Kkt.objects.filter(fn_number=fn_number_in_msg(msg_text)).first()
        if kkts is None:
            return {"text": "Кассы с таким номером ФН нет в базе. Необходимо добавить кассу на сайте",
                    "markup": None}
        else:
            # Создание нового чека
            new_check = Check_kkt(
                kkt=kkts,
                cash=0,
                ecash=0,
                buyer_name='',
                status='Создание телеграмм'
            )
            new_check.save()
            # Отмечаем чек к пользователю
            bot_user.current_сheck = new_check
            # перходим на следующий шаг бот-пользователя
            bot_user.bot_user_status = 'Выбор номенклатуры'
            bot_user.save()
            # Запрос списка названий номенклатуры
            goods_name_choice = new_check._get_kkt_goods()
            goods_name_choice.extend(['Отмена', 'Добавить новую'])
            return {"text": "Выберете номенклатуру",
                    "markup": goods_name_choice}
    return {"text": 'Введите номер ФН кассы',
            "markup": None}


def goods_name(bot_user, msg_text):
    """Определение названия номенклатуры в чек"""
    if msg_text.strip() == 'Добавить новую':
        # перходим на следующий шаг бот-пользователя
        bot_user.bot_user_status = 'Новая номенклатура'
        bot_user.save()
        return {"text": 'Введите новое наименование номенклатуры.',
                "markup": ['Отмена']}
    new_check_goods = Check_good(
            check_kkt=bot_user.current_сheck,
            product_name=msg_text.strip(),
            price=0
        )
    new_check_goods.save()
    # Новая позиция номенклатуры в чек
    bot_user.current_goods = new_check_goods
    # перходим на следующий шаг бот-пользователя
    bot_user.bot_user_status = 'Количество номенклатуры'
    bot_user.save()
    return {"text": 'Введите количество',
            "markup": ['Отмена']}


def goods_qty(bot_user, msg_text):
    """Определение количества номенклатуры в чек"""
    if qty_in_msg(msg_text):
        bot_user.current_goods.qty = qty_in_msg(msg_text)
        bot_user.current_goods.save()
        # перходим на следующий шаг бот-пользователя
        bot_user.bot_user_status = 'Выбор ставки налога'
        bot_user.save()
        # список ставок ндс
        tax_choice = ['Отмена']
        tax_choice.extend([val[1] for val in Check_good.Tax.choices])
        return {"text": 'Выберите ставку налога',
                "markup": tax_choice}
    return {"text": 'Введите количество',
            "markup": None}


def goods_tax_code(bot_user, msg_text):
    """Определение ставки НДС номенклатуры в чек"""
    for tax in Check_good.Tax.choices:
        if msg_text.strip().lower() == tax[1].replace('_', ' ').lower():
            bot_user.current_goods.tax_code = tax[0]
            bot_user.current_goods.save()
            # перходим на следующий шаг бот-пользователя
            bot_user.bot_user_status = 'Ввод цены номенклатуры'
            bot_user.save()
            return {"text": 'Введите цену за единицу',
                    "markup": ['Отмена']}
    return {"text": 'Выберете ставку налога',
            "markup": None}


def goods_price(bot_user, msg_text):
    """Определение цены за единицу номенклатуры в чек"""
    if summ_in_msg(msg_text):
        bot_user.current_goods.price = summ_in_msg(msg_text)
        bot_user.current_goods.save()
        # перходим на следующий шаг бот-пользователя
        bot_user.bot_user_status = 'Выбор предмета расчёта'
        bot_user.save()
        # список предметов расчёта
        product_type_choice = ['Отмена']
        product_type_choice.extend([val[1] for val in Check_good.Product_type.choices])
        return {"text": 'Выберите предмет расчёта',
                "markup": product_type_choice}
    return {"text": 'Введите цену за единицу номенклатуры',
            "markup": None}


def goods_product_type_code(bot_user, msg_text):
    """Выбор предмета расчёта"""
    for type_code in Check_good.Product_type.choices:
        if msg_text.strip() == type_code[1]:
            bot_user.current_goods.product_type_code = type_code[0]
            bot_user.current_goods.save()
            # перходим на следующий шаг бот-пользователя
            bot_user.bot_user_status = 'Выбор оплата или дополнение'
            bot_user.save()
            return {"text": 'Принять оплату или добавить ещё номенклатуру.',
                    "markup": ['Добавить номенклатуру', 'Принять оплату', 'Отмена']}
    return {"text": 'Выбирайте предмет расчёта из списка',
            "markup": None}


def payment_or_goods_adding(bot_user, msg_text):
    """Выбор добавить номенклатуру ещё или принять оплату"""
    if msg_text == 'Добавить номенклатуру':  # Добавить ещё номенклатуру
            # перходим на следующий шаг бот-пользователя
            bot_user.bot_user_status = 'Выбор номенклатуры'
            bot_user.save()
            # Запрос списка названий номенклатуры
            goods_name_choice = bot_user.current_сheck._get_kkt_goods()
            goods_name_choice.extend(['Отмена', 'Добавить новую'])
            return {"text": "Выберете номенклатуру",
                    "markup": goods_name_choice}
    elif msg_text == 'Принять оплату':  # Принять оплату
            # перходим на следующий шаг бот-пользователя
            bot_user.bot_user_status = 'Выбор типа оплаты'
            bot_user.save()
            return {"text": "Выберете тип оплаты",
                    "markup": ['Наличными', 'Безналичные']}
    else:
        return {"text": 'Выбирайте действие из списка',
                "markup": None}


def payment_type(bot_user, msg_text):
    """Выбор типа оплаты"""
    if msg_text == 'Наличными':  # Оплата наличными
            # перходим на следующий шаг бот-пользователя
            bot_user.bot_user_status = 'Ввод суммы оплаты наличными'
            bot_user.save()
            # получение суммы из суммы списка товаров
            summ_of_check = bot_user.current_сheck._get_goods_summ()

            return {"text": "Выведите сумму оплаты наличными",
                    "markup": ['Безналичными', str(summ_of_check)[:-2]+'.'+str(summ_of_check)[-2:]]}
    elif msg_text == 'Безналичные':  # Оплата безналичными
            # перходим на следующий шаг бот-пользователя
            bot_user.bot_user_status = 'Ввод суммы оплаты безналичными'
            bot_user.save()
            # получение суммы из суммы списка товаров
            summ_of_check = bot_user.current_сheck._get_goods_summ()
            return {"text": "Введите сумму оплаты безналичными",
                    "markup": ['Наличными', str(summ_of_check)[:-2]+'.'+str(summ_of_check)[-2:], 'QR-код квитанции']}
    else:
        return {"text": 'Выбирайте действие из списка',
                "markup": None}


def cash_payment(bot_user, msg_text):
    """Определение суммы оплаты наличными в чек"""
    if summ_in_msg(msg_text):
        bot_user.current_сheck.cash = summ_in_msg(msg_text)
        bot_user.current_сheck.save()
        # Сумма номенклатуры в чеке
        summ_of_check = bot_user.current_сheck._get_goods_summ()
        if summ_of_check <= summ_in_msg(msg_text):
            # если меньше суммы оплаты перходим на следующий шаг бот-пользователя
            bot_user.bot_user_status = 'Ввод наименования покупателя'
            bot_user.save()
            # список покупателей
            buyer_name_choice = ['Пропустить', 'Добавить нового']
            buyer_name_choice.extend(bot_user.current_сheck._get_kkt_buyer().values())
            return {"text": 'Выберите покупателя',
                    "markup": buyer_name_choice}
    elif msg_text == 'Безналичные':  # Оплата безналичными
            # перходим на следующий шаг бот-пользователя
            bot_user.bot_user_status = 'Ввод суммы оплаты безналичными'
            bot_user.save()
            # получение суммы из суммы списка товаров
            summ_of_check = bot_user.current_сheck._get_goods_summ()
            return {"text": "Введите сумму оплаты безналичными",
                    "markup": ['Наличными', str(summ_of_check)[:-2]+'.'+str(summ_of_check)[-2:], 'QR-код квитанции']}
    return {"text": 'Введите сумму оплаты наличными. Сумма оплаты должна быть больше суммы номенклатуры чека.',
            "markup": None}


def ecash_payment(bot_user, msg_text):
    """Определение суммы оплаты безналичными в чек"""
    if summ_in_msg(msg_text):
        bot_user.current_сheck.ecash = summ_in_msg(msg_text)
        bot_user.current_сheck.save()
        # Сумма номенклатуры в чеке
        summ_of_check = bot_user.current_сheck._get_goods_summ()
        if summ_of_check <= summ_in_msg(msg_text):
            # если меньше суммы оплаты перходим на следующий шаг бот-пользователя
            bot_user.bot_user_status = 'Ввод наименования покупателя'
            bot_user.save()
            # список покупателей
            buyer_name_choice = ['Пропустить', 'Добавить нового']
            buyer_name_choice.extend(bot_user.current_сheck._get_kkt_buyer().values())
            return {"text": 'Выберите покупателя',
                    "markup": buyer_name_choice}
    elif msg_text == 'Наличными':  # Оплата наличными
            # перходим на следующий шаг бот-пользователя
            bot_user.bot_user_status = 'Ввод суммы оплаты наличными'
            bot_user.save()
            # получение суммы из суммы списка товаров
            summ_of_check = bot_user.current_сheck._get_goods_summ()
            return {"text": "Введите сумму оплаты наличными",
                    "markup": ['Безналичными', str(summ_of_check)[:-2]+'.'+str(summ_of_check)[-2:]]}
    return {"text": 'Введите сумму оплаты банковской картой или через расчётный счёт.\
                     Сумма оплаты должна быть больше суммы номенклатуры чека.',
            "markup": None}


def buyer_name(bot_user, msg_text):
    """Ввод наименование покупателя в чек"""
    # Ищем наименование покупателя в чеках и сверяем с введеным именем, из этого же словаря берем инн
    for buyer_inn, buyer_name in bot_user.current_сheck._get_kkt_buyer().items():
        if msg_text.strip() == buyer_name:
            bot_user.current_сheck.buyer_name = buyer_name
            bot_user.current_сheck.buyer_inn = buyer_inn
            bot_user.bot_user_status = 'Ввод адреса покупателя'
            bot_user.current_сheck.save()
            bot_user.save()
            buyer_emails = ['Пропустить']
            buyer_emails.extend(bot_user.current_сheck._get_kkt_buyer_email())
            return {"text": "Введите e-mail адрес отправки электронного чека",
                    "markup": buyer_emails}
    if msg_text.strip() == 'Добавить нового':
        # Добавление нового покупателя
        bot_user.bot_user_status = 'Ввод нового покупателя'
        bot_user.save()
        return {"text": "Введите название покупателя и ИНН (10 или 12 цифр)",
                "markup": ['Пропустить']}
    elif msg_text.strip() == 'Пропустить':
        # Переход на ввод адреса получателя чека
        bot_user.bot_user_status = 'Ввод адреса покупателя'
        bot_user.save()
        return {"text": "Введите e-mail адрес отправки электронного чека",
                "markup": ['Пропустить']}
    return {"text": 'Выберите название покупателя или добавтье нового.',
            "markup": None}


def add_new_buyer(bot_user, msg_text):
    """Ввод нового покупателя в чек"""
    # Ищем наименование покупателя и инн из сообщения
    if msg_text.strip() != 'Пропустить':
            bot_user.current_сheck.buyer_name = name_and_inn_in_msg(msg_text)['name']
            bot_user.current_сheck.buyer_inn = name_and_inn_in_msg(msg_text)['inn']
            bot_user.bot_user_status = 'Ввод адреса покупателя'
            bot_user.current_сheck.save()
            bot_user.save()
            buyer_emails = ['Пропустить']
            buyer_emails.extend(bot_user.current_сheck._get_kkt_buyer_email())
            return {"text": "Введите e-mail адрес отправки электронного чека",
                    "markup": buyer_emails}
    if msg_text.strip() == 'Пропустить':
        # Переход на ввод адреса получателя чека
        bot_user.bot_user_status = 'Ввод адреса покупателя'
        bot_user.save()
        return {"text": "Введите e-mail адрес отправки электронного чека",
                "markup": ['Пропустить']}
    return {"text": 'Введите название покупателя или добавтье нового.',
            "markup": None}


def send_check_to(bot_user, msg_text):
    """Ввод адреса отправки в чек"""
    if email_in_msg(msg_text.strip()):
        bot_user.current_сheck.send_check_to = msg_text.strip()
        bot_user.current_сheck.save()
        # Переход на выбор системы налогообложения в чек
        bot_user.bot_user_status = 'Выбор системы налогообложения'
        bot_user.save()
        # список систем налогообложения из модели чека
        return {"text": 'Выберите систему налогообложения',
                "markup": [val[1] for val in Check_kkt.Taxsystem.choices]}
    elif msg_text.strip() == 'Пропустить':
        bot_user.bot_user_status = 'Выбор системы налогообложения'
        bot_user.save()
        # список систем налогообложения из модели чека
        return {"text": 'Выберите систему налогообложения',
                "markup": [val[1] for val in Check_kkt.Taxsystem.choices]}
    return {"text": 'Введите адрес электронной почты example@site.ru',
            "markup": None}


def tax_system(bot_user, msg_text):
    """Выбор системы налогообложения в чеке"""
    for tax_system_code in Check_kkt.Taxsystem.choices:
        if msg_text.strip() == tax_system_code[1]:
            bot_user.current_сheck.tax_system = tax_system_code[0]
            bot_user.current_сheck.save()
            # перходим на следующий шаг бот-пользователя
            bot_user.bot_user_status = 'Вывод окончательного варианта чека'
            bot_user.save()
            text_of_check = bot_user.current_сheck.get_text_of_check()
            return {"text": f'Проверьте реквизиты чека.\n {text_of_check}',
                    "markup": ['Регистрация чека', 'Аннулировать чек']}
    return {"text": 'Зарегистрировать чек или аннулировать',
            "markup": None}


def finish_check(bot_user, msg_text):
    """Подтверждение чека перед регистрацией на сервере"""
    if msg_text.strip() == 'Аннулировать чек':
        bot_user.current_сheck.status = 'Аннулирован'
        bot_user.current_сheck.save()
        # Возврат на этап выбора действий пользователя
        bot_user.bot_user_status = 'Выбор'
        bot_user.save()
        return {"text": "Пользователь авторизован.\nВыберете действие:",
                "markup": ['Чек прихода', 'Отмена']}
    elif msg_text.strip() == 'Регистрация чека':
        bot_user.current_сheck.status = 'Добавлен'
        bot_user.current_сheck.save()
        bot_user.bot_user_status = 'Выбор'
        bot_user.save()
        return {"text": "Пользователь авторизован.\nВыберете действие:",
                "markup": ['Чек прихода', 'Отмена']}
    return {"text": 'Зарегистрировать чек или аннулировать?',
            "markup": None}


user_command_status = {
    # логика диалога бота
    'Авторизация': bot_autorisation,
    'Проверка регистрации': check_bot_autorisation,
    'Пароль': login_pass,
    'Выбор': bot_menu,
    'Выбор кассы': bot_check_kkt,
    'Выбор номенклатуры': goods_name,
    'Новая номенклатура': goods_name,
    'Количество номенклатуры': goods_qty,
    'Выбор ставки налога': goods_tax_code,
    'Ввод цены номенклатуры': goods_price,
    'Выбор предмета расчёта': goods_product_type_code,
    'Выбор оплата или дополнение': payment_or_goods_adding,
    'Выбор типа оплаты': payment_type,
    'Ввод суммы оплаты наличными': cash_payment,
    'Ввод суммы оплаты безналичными': ecash_payment,
    'Ввод наименования покупателя': buyer_name,
    'Ввод нового покупателя': add_new_buyer,
    'Ввод адреса покупателя': send_check_to,
    'Выбор системы налогообложения': tax_system,
    'Вывод окончательного варианта чека': finish_check
}