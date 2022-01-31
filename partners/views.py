from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail, BadHeaderError
from .forms import PartnerProfileEditForm, NewContractForm, PaymentContractForm, MakeCodeOrderForm
from .models import Partnerprofile, Contract, PaymentCode, CodeOrder
from kkt_check.models import Kkt
from users.models import Profile
from django.contrib.auth.decorators import login_required
from django.http import Http404
from mngcheck.settings import DEFAULT_FROM_EMAIL
from icecream import ic


def payment_code_generator(user, num_codes, mounth_payment_count):  # Возвращает список кодов
    """Генератор кодов оплаты для пртнера"""
    i = 0
    code_list = []
    while i < num_codes:
        new_code = PaymentCode()
        new_code.owner = user
        new_code.mounth_payment_count = mounth_payment_count
        new_code.save()
        code_list.append(new_code.code)
        i += 1
    return code_list

def send_order_msg(user, num_codes):
    """Отправка сообщения ,что пользователь создал заказ на коды"""
    subject = f'Заказ на коды активации от {user.profile.legal_entity}'
    message = f'На ИНН {user.partnerprofile.inn} неоходимо выписать {num_codes} кодов.'
    try:
        dilers = Profile.objects.filter(client_status=2)
    except:
        return HttpResponse('Не найден адрес дилера')
    diler_email = []
    for diler in dilers:
        diler_email.append(diler.user.email)
    try:
        send_mail(subject, message,
                  DEFAULT_FROM_EMAIL, diler_email)
    except BadHeaderError:
        return HttpResponse('Ошибка в теме письма.')


def send_codes_msg(user, code_list):
    """Отправка сообщения с кодами заказа"""
    subject = f'Коды активации для {user.profile.legal_entity}'
    codes = '\n'.join(code_list)
    message = f'Выпущено {len(code_list)} кодов. {codes}'
    try:
        send_mail(subject, message,
                  DEFAULT_FROM_EMAIL, [user.email])
    except BadHeaderError:
        return HttpResponse('Ошибка в теме письма.')


@login_required
def contracts(request):
    """Выводит список контрактов партнера."""
    contract_list = Contract.objects.filter(owner=request.user).order_by('date_added')
    context = {'contract_list': contract_list}
    return render(request, 'partners/contracts.html', context)


@login_required
def new_contract(request):
    """Добавление клиента к партнеру"""
    if request.method != 'POST':
        # Данные не отправлялись; создается пустая форма.
        form = NewContractForm()
    else:
        # Отправлены данные POST; обработать данные.
        form = NewContractForm(data=request.POST)
        if form.is_valid():
            owner = request.user
            kkt = Kkt.objects.get(fn_number=form.cleaned_data['fn_number'])
            new_contract = Contract(owner=owner, kkt=kkt)
            new_contract.save()
            return redirect('partners:contracts')
    # Вывести пустую или недействительную форму.
    context = {'form': form}
    return render(request, 'partners/new_contract.html', context)


@login_required
def view_contract(request, contract_id):
    """Просмотр существующего клиента у партнера."""
    try:
        contract = Contract.objects.get(id=contract_id)
    except contract.DoesNotExist:
        raise Http404
    if contract.owner != request.user:
        raise Http404
    kkt = contract.kkt
    context = {'kkt': kkt, 'contract': contract}
    return render(request, 'partners/view_contract.html', context)


@login_required
def del_contract(request, contract_id):
    """Удаление существующего контракта"""
    try:
        contract = Contract.objects.get(id=contract_id)
    except Contract.DoesNotExist:
        raise Http404
    if contract.owner != request.user:
        raise Http404
    contract.delete()
    return redirect('partners:contracts')


@login_required
def payment_contract(request, contract_id):
    """Меняет дату действия тарифа при вводе кода активации"""
    try:
        contract = Contract.objects.get(id=contract_id)
    except Contract.DoesNotExist:
        raise Http404
    if contract.owner != request.user:
        raise Http404
    if request.method == 'POST':
        # Отправка данных POST; обработать данные.
        form = PaymentContractForm(data=request.POST)
        if form.is_valid():
            # Получение проверенного кода из формы
            code = form.cleaned_data.get('payment_code')
            # Поиск кода в БД
            payment_code = PaymentCode.objects.get(code=code)
            # Оплата контракта
            contract.pay_contract(payment_code.mounth_payment_count)
            contract.save()
            payment_code.delete()
            return redirect('partners:view_contract', contract_id=contract.id)
    else:
        form = PaymentContractForm()
    context = {'contract': contract, 'form': form}
    return render(request, 'partners/payment_contract.html', context)


@login_required
def view_payment_codes(request):
    """Просмотр и работа с кодами активации"""
    try:
        code_count = PaymentCode.objects.filter(owner=request.user).count
    except PaymentCode.DoesNotExist:
        code_count = 0

    context = {'code_count': code_count}
    return render(request, 'partners/view_payment_codes.html', context)


@login_required
def make_oder(request):
    """Формирование заявки на приобретение пртнером кодов активации"""
    if request.method == 'POST':
        # Отправка данных POST; обработать данные.
        form = MakeCodeOrderForm(data=request.POST)
        if form.is_valid():
            # Получение проверенного кода из формы
            num_code = form.cleaned_data.get('num_payment_code')
            mounth_payment_count = form.cleaned_data.get('mounth_payment_count')
            # Проверка пользователя статуса
            if request.user.profile.client_status == 1:
                # Отправка сообщения о необходимом заказе
                send_order_msg(request.user, num_code)
                # Создание заказа дилеру
                new_order = CodeOrder()
                new_order.owner = request.user
                new_order.mounth_payment_count = mounth_payment_count
                new_order.code_count = num_code
                new_order.save()
            return redirect('partners:view_payment_codes')
    else:
        form = MakeCodeOrderForm()
    context = {'form': form}
    return render(request, 'partners/make_oder.html', context)


@login_required
def partners(request):
    """Выводит список партнеров"""
    partners_list = Partnerprofile.objects.order_by('inn')
    context = {'partners_list': partners_list}
    return render(request, 'partners/partners.html', context)


@login_required
def view_order(request, partner_id):
    """Выводит заказы партнера."""
    try:
        partner = Partnerprofile.objects.get(id=partner_id)
    except Partnerprofile.DoesNotExist:
        raise Http404
    orders = CodeOrder.objects.filter(owner=partner.user).order_by('-date_added')
    context = {'partner': partner, 'orders': orders}
    return render(request, 'partners/view_order.html', context)


@login_required
def del_order(request, order_id):
    """Удаление существующего заказа"""
    try:
        order = CodeOrder.objects.get(id=order_id)
    except CodeOrder.DoesNotExist:
        raise Http404
    if request.user.profile.client_status != 2:
        raise Http404
    partner = Partnerprofile.objects.get(user=order.owner)
    order.delete()
    return redirect('partners:view_order', partner_id=partner.id)


@login_required
def order_send(request, order_id):
    """Формирование кодов активации и отправка их партнеру по заказу"""
    try:
        order = CodeOrder.objects.get(id=order_id)
    except CodeOrder.DoesNotExist:
        raise Http404
    if request.user.profile.client_status != 2:
        raise Http404
    # партнер получатель заказа
    partner = Partnerprofile.objects.get(user=order.owner)
    # генерация кодов
    code_list = payment_code_generator(order.owner, order.code_count, order.mounth_payment_count)
    # отправка кодов по почте
    send_codes_msg(order.owner, code_list)
    # смена статуса заказа
    order.payment_status = 'Отправлен'
    order.save()
    return redirect('partners:view_order', partner_id=partner.id)