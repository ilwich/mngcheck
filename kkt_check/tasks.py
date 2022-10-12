from django.template import Template, Context
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
import datetime
from dateutil.relativedelta import relativedelta
import pytz
from mngcheck.celery import app
from .models import Kkt
from partners.models import Contract, Partnerprofile
from users.models import Profile
from icecream import ic


# Шаблоны тела письмо об окончании оплаты
MOUNTH_REPORT_TEMPLATE = """
Состояние тарифов по Вашим кассам:
до окончания оплаченного периода остался 1 месяц
        Тариф по кассе {{ kkt.name }}: действует до {{ kkt.data_end_of_payment }} |
Для продления тарифа обратитесь к партнёру 
{{ partner_info.name }} 
контактные данные 
{{ partner_info.contacts }}
"""
THREEDAY_REPORT_TEMPLATE = """
Состояние тарифов по Вашим кассам:
до окончания оплаченного периода осталось три дня
        Тариф по кассе {{ kkt.name }}: действует до {{ kkt.data_end_of_payment }} |
Для продления тарифа обратитесь к партнёру 
{{ partner_info.name }} 
контактные данные 
{{ partner_info.contacts }}
"""
ENDOFPAY_REPORT_TEMPLATE = """
Состояние тарифов по Вашим кассам:
Оплаченный период окончен
        Тариф по кассе {{ kkt.name }}: действует до {{ kkt.data_end_of_payment }} |
Для продления тарифа обратитесь к партнёру 
{{ partner_info.name }} 
контактные данные 
{{ partner_info.contacts }}
"""

MOUNTH_CONTRACTS_REPORT_TEMPLATE = """
Состояние котрактов по Вашим клиентам:
До окончания оплаченного периода остался 1 месяц
   {% for contract in contract_info %}
     {{ contract }}
   {% endfor %}
        
Для продления тарифа свяжитесь с клиентом 

"""

THREEDAY_CONTRACTS_REPORT_TEMPLATE = """
Состояние котрактов по Вашим клиентам:
До окончания оплаченного периода осталось три дня
   {% for contract in contract_info %}
     {{ contract }}
   {% endfor %}

Для продления тарифа свяжитесь с клиентом 

"""
ENDOFPAY_CONTRACTS_REPORT_TEMPLATE = """
Состояние котрактов по Вашим клиентам:
Окончился оплаченный период на кассах
   {% for contract in contract_info %}
     {{ contract }}
   {% endfor %}

Для продления тарифа свяжитесь с клиентом 

"""


def get_parner_info_by_kkt(kkt):
    """Получаем данные партнера по кассе"""
    # определение наименования и контактов партнера по предыдущим контрактам кассы
    partner_contracts = Contract.objects.filter(kkt=kkt).order_by('-date_end_payment')
    if partner_contracts.count() != 0:
        partner_profiles = Partnerprofile.objects.filter(user=partner_contracts[0].owner)
        if partner_profiles.count() != 0:
            for partner_profile in partner_profiles:
                return {
                    'name': f'{partner_profile}',
                    'contacts': partner_profile.contacts}
    # если контрактов нет то отправляем данные основного партнера
    else:
        partner_profile = Partnerprofile.objects.all()[0]
        return {
            'name': f'{partner_profile}',
            'contacts': partner_profile.contacts}
    return {'name': None, 'contracts': None}


def client_info_by_kkt(kkt):
    """Возвращаем информацию о пользователе по кассе"""
    client = Profile.objects.get(user=kkt.owner)
    return f'Клиент: {client.legal_entity}. \n Касса: {kkt}'

def contracts_send_mail(template, contract_info_list, email):
    if contract_info_list:
        send_mail(
                    'Статусы оплаты у Ваших клиентов по тарифам в сервисе Kassbot',
                    template.render(context=Context({'contract_info': contract_info_list})),
                    'buh@5element35.ru',
                    [email],
                    fail_silently=False,
                )



@app.task
def send_view_count_report():
    """Задание на отправку предупреждений по электронной почте пользователя об окончании оплаты тарифа за месяц, три дня
    и полном окончании оплаты"""
    date_now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC).date()
    for user in get_user_model().objects.all():
        kkts = Kkt.objects.filter(owner=user)

        if kkts.count() == 0:
            continue
        # если кассы у пользователя присутствуют смотрим даты окончания за месяц
        partner_info = {}
        for kkt in kkts:
            if date_now == (kkt.data_end_of_payment+relativedelta(months=-1)).date():
                # шаблон для формирования сообщения в тело письма об окончании периода оплаты за месяц
                template = Template(MOUNTH_REPORT_TEMPLATE)
                # определение наименования и контактов партнера по предыдущим контрактам кассы
                partner_info = get_parner_info_by_kkt(kkt)
            elif date_now == (kkt.data_end_of_payment+relativedelta(days=-3)).date():
                # шаблон для формирования сообщения в тело письма об окончании периода оплаты за Три дня
                template = Template(THREEDAY_REPORT_TEMPLATE)
                # определение наименования и контактов партнера по предыдущим контрактам кассы
                partner_info = get_parner_info_by_kkt(kkt)
            elif date_now == kkt.data_end_of_payment.date():
                # шаблон для формирования сообщения в тело письма об окончании периода оплаты
                template = Template(ENDOFPAY_REPORT_TEMPLATE)
                # определение наименования и контактов партнера по предыдущим контрактам кассы
                partner_info = get_parner_info_by_kkt(kkt)

            else:
                continue
            send_mail(
                    'Действие тарифа в сервисе Kassbot',
                    template.render(context=Context({'kkt': kkt, 'partner_info': partner_info})),
                    'buh@5element35.ru',
                    [user.email],
                    fail_silently=False,
                )

@app.task
def send_contact_count_report():
    """ОТправка сообщений партнёрам об окончании оплаты контрактов пользователей за месяц , три дня и окончании"""
    date_now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC).date()
    for partner in Partnerprofile.objects.all():

        kkts = Kkt.objects.filter(owner=partner.user)

        if kkts.count() == 0:
            continue
        # если кассы у пользователя присутствуют смотрим даты окончания по трём критериям
        contract_info = {
            'mount_contracts': [],
            'threeday_contracts': [],
            'endpay_contracts': []
        }
        for kkt in kkts:
            if date_now == (kkt.data_end_of_payment+relativedelta(months=-1)).date():
                contract_info['mount_contracts'].append(client_info_by_kkt(kkt))
            elif date_now == (kkt.data_end_of_payment+relativedelta(days=-3)).date():
                contract_info['threeday_contracts'].append(client_info_by_kkt(kkt))
            elif date_now == kkt.data_end_of_payment.date():
                contract_info['endpay_contracts'].append(client_info_by_kkt(kkt))
            else:
                continue
        # отправка отчета о тарифах оканчивающихся через месяц
        contracts_send_mail(Template(MOUNTH_CONTRACTS_REPORT_TEMPLATE),
                            contract_info['mount_contracts'],
                            partner.user.email)
        # отправка отчета о тарифах оканчивающихся через три дня
        contracts_send_mail(Template(THREEDAY_CONTRACTS_REPORT_TEMPLATE),
                            contract_info['threeday_contracts'],
                            partner.user.email)
        # отправка отчета о тарифах оканчивающихся сегодня
        contracts_send_mail(Template(ENDOFPAY_CONTRACTS_REPORT_TEMPLATE),
                            contract_info['endpay_contracts'],
                            partner.user.email)

