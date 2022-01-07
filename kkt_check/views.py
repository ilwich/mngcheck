from django.shortcuts import render, redirect
from icecream import ic
import collections
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404
from .models import Kkt, Check_kkt, Check_good
from bot.views import send_reply_telebot, send_qr_check_telebot
from .serializers import KktSerializer, CheckSerializer, GoodSerializer
from .forms import KktForm, CheckForm, GoodForm
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.http.response import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
import os
from re import findall


def telegram_id_in_msg(str_in):
    """Выдели teleramm id из сообщении"""
    pattern = '(\d+$)'
    res = findall(pattern, str_in)
    if res:
        return int(res[-1])
    else:
        return False


class GetKktInfoView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        # Получаем набор всех записей из таблицы Kkt
        queryset = Kkt.objects.order_by('date_added')
        # Сериализуем извлечённый набор записей
        serializer_for_queryset = KktSerializer(
            instance=queryset, # Передаём набор записей
            many=True # Указываем, что на вход подаётся именно набор записей
        )
        return Response(serializer_for_queryset.data)


class GetKktDetail(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, fn_number):
        # Получаем Kkt по значению заводского номера ФН
        try:
            kkt = Kkt.objects.get(fn_number=fn_number)
        except Kkt.DoesNotExist:
            return JsonResponse({'message': 'The kkt does not exist'}, status=status.HTTP_404_NOT_FOUND)
        # Сериализуем извлечённую запись
        serializer_for_queryset = KktSerializer(kkt)
        return Response(serializer_for_queryset.data)

    def put(self, request, fn_number):
        kkt_saved = get_object_or_404(Kkt.objects.all(), fn_number=fn_number)
        data = request.data.get('kkt')
        serializer = KktSerializer(instance=kkt_saved, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            saved_kkt = serializer.save()
        return Response({
            "success": "KKT '{}' updated successfully".format(saved_kkt.fn_number)
        })


class GetCheckInfoView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, fn_number):
        # Получаем чеки по значению заводского номера ФН со статусом Добавлен
        try:
            kkt = Kkt.objects.get(fn_number=fn_number)
        except Kkt.DoesNotExist:
            return JsonResponse({'message': 'The kkt does not exist'}, status=status.HTTP_404_NOT_FOUND)
        kkt_checks = kkt.check_kkt_set.filter(status='Добавлен').order_by('-date_added').values()

        # Сериализуем извлечённую запись
        serializer_for_queryset = CheckSerializer(kkt_checks, many=True)
        return Response(serializer_for_queryset.data)

    def put(self, request, fn_number):
        # Обновляем данные кассы по значению заводского номера ФН со статусом Добавлен
        try:
            kkt_saved = Kkt.objects.get(fn_number=fn_number)
        except Kkt.DoesNotExist:
            return JsonResponse({'message': 'The kkt does not exist'}, status=status.HTTP_404_NOT_FOUND)
        kkt_checks = kkt_saved.check_kkt_set.filter(status='Добавлен').order_by('-date_added').values()
        data = request.data.get('kkt')
        serializer = KktSerializer(instance=kkt_checks, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            saved_kkt = serializer.save()
        return Response({
            "success": "KKT '{}' updated successfully".format(saved_kkt.fn_number)
        })


class GetCheckDetail((APIView)):
    permission_classes = (IsAuthenticated,)

    def get(self, request, fn_number, date_added):
        # Получаем чек по значению заводского номера ФН и по дате создания
        try:
            kkt = Kkt.objects.get(fn_number=fn_number)
        except Kkt.DoesNotExist:
            return JsonResponse({'message': 'The kkt does not exist'}, status=status.HTTP_404_NOT_FOUND)
        kkt_check = kkt.check_kkt_set.filter(date_added=date_added)
        # Сериализуем извлечённые записи
        serializer_for_queryset = CheckSerializer(kkt_check.values(), many=True)
        outdata = serializer_for_queryset.data
        # Получаем список товаров по чеку
        good_serialiser_for_queryset = GoodSerializer(kkt_check[0].checkkktset.all().values(), many=True)
        # Добавляем словарь с данными о товарах в информацию о чеке
        outdata[0]['goods'] = good_serialiser_for_queryset.data
        return Response(outdata)

    def put(self, request, fn_number, date_added):
        # Обновляем данные чека по значению заводского номера ФН и по дате создания
        kkt_saved = get_object_or_404(Kkt.objects.all(), fn_number=fn_number)
        kkt_check = kkt_saved.check_kkt_set.filter(date_added=date_added)
        data = request.data.get('check')
        for check in kkt_check:
            serializer = CheckSerializer(instance=check, data=data, partial=True)
            serializer.is_valid()
            if serializer.is_valid(raise_exception=True):
                saved_check = serializer.save()
                # Проверка на ответ в месседжер
                if 'telegram' in saved_check.bot_message_id:  # если чек из телеграмм, то ответить по id пользователя
                    update_id = telegram_id_in_msg(saved_check.bot_message_id)
                    if update_id:
                        send_reply_telebot(str(saved_check), update_id)
                        send_qr_check_telebot(saved_check.status, update_id)
            return Response({
                "success": f"Check '{saved_check.date_added}' updated successfully"
            })


# Create your views here.

def index(request):
    """Домашняя страница приложения kkt-check"""
    return render(request, 'kkt_check/index.html')


@login_required
def kktlist(request):
    """Выводит список касс."""
    kkt_list = Kkt.objects.filter(owner=request.user).order_by('date_added')
    context = {'kkt_list': kkt_list}
    return render(request, 'kkt_check/kktlist.html', context)


@login_required
def kkt(request, kkt_id):
    """Выводит одну кассу и все ее чеки."""
    try:
        kkt = Kkt.objects.get(id=kkt_id)
    except Kkt.DoesNotExist:
        raise Http404
    # Проверка того, что ккт принадлежит текущему пользователю.
    if kkt.owner != request.user:
        raise Http404
    kkt_checks = kkt.check_kkt_set.order_by('-date_added')
    context = {'kkt': kkt, 'kkt_checks': kkt_checks}
    return render(request, 'kkt_check/kkt.html', context)


@login_required
def new_kkt(request):
    """Определяет новую кассу."""
    if request.method != 'POST':
        # Данные не отправлялись; создается пустая форма.
        form = KktForm()
    else:
        # Отправлены данные POST; обработать данные.
        form = KktForm(data=request.POST, initial={'retry': 1, 'delay': 2})
        if form.is_valid():
            new_kkt = form.save(commit=False)
            new_kkt.owner = request.user
            new_kkt.save()
            return redirect('kkt_check:kktlist')
    # Вывести пустую или недействительную форму.
    context = {'form': form}
    return render(request, 'kkt_check/new_kkt.html', context)


@login_required
def edit_kkt(request, kkt_id):
    """Редактирует существующую кассу."""
    try:
        kkt = Kkt.objects.get(id=kkt_id)
    except Kkt.DoesNotExist:
        raise Http404
    if kkt.owner != request.user:
        raise Http404
    if request.method != 'POST':
        # Исходный запрос; форма заполняется данными текущей записи.
        form = KktForm(instance=kkt)
    else:
        # Отправка данных POST; обработать данные.
        form = KktForm(instance=kkt, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('kkt_check:kkt', kkt_id=kkt.id)
    context = {'kkt': kkt, 'form': form}
    return render(request, 'kkt_check/edit_kkt.html', context)


@login_required
def del_kkt(request, kkt_id):
    """Удаление существующей кассы."""
    try:
        kkt = Kkt.objects.get(id=kkt_id)
    except Kkt.DoesNotExist:
        raise Http404
    if kkt.owner != request.user:
        raise Http404
    kkt.delete()
    return redirect('kkt_check:kktlist')


@login_required
def new_check_kkt(request, kkt_id):
    """Добавляет новый чек по конкретной ккт."""
    try:
        kkt = Kkt.objects.get(id=kkt_id)
    except Kkt.DoesNotExist:
        raise Http404
    if request.method != 'POST':
        # Данные не отправлялись; создается пустая форма.
        form = CheckForm()
    else:
        # Отправлены данные POST; обработать данные.
        form = CheckForm(data=request.POST)
        if form.is_valid():
            new_check_kkt = form.save(commit=False)
            new_check_kkt.kkt = kkt
            new_check_kkt.save()
            return redirect('kkt_check:kkt', kkt_id=kkt_id)
    # Вывести пустую или недействительную форму.
    context = {'kkt': kkt, 'form': form}
    return render(request, 'kkt_check/new_check_kkt.html', context)


@login_required
def edit_check_kkt(request, check_kkt_id):
    """Редактирует существующий чек."""
    try:
        check_kkt = Check_kkt.objects.get(id=check_kkt_id)
        kkt = check_kkt.kkt
    except Check_kkt.DoesNotExist:
        raise Http404
    kkt_check_goods_val = check_kkt.checkkktset.all().values()
    sum_cash_in_goods = sum((good['price'] * good['qty']) / 10000 for good in kkt_check_goods_val)
    if kkt.owner != request.user:
        raise Http404
    if request.method != 'POST':
        # Исходный запрос; форма заполняется данными текущей записи.
        form = CheckForm(instance=check_kkt)
    else:
        # Отправка данных POST; обработать данные.
        form = CheckForm(instance=check_kkt, data=request.POST)
        if form.is_valid():
            cash = form.cleaned_data.get("cash")
            ecash = form.cleaned_data.get("ecash")
            if sum_cash_in_goods > (ecash + cash):
                msg = "Сумма типов оплат меньше суммы позиций чека."
                form.add_error('cash', msg)
                form.add_error('ecash', msg)
            else:
                form.save()
                return redirect('kkt_check:kkt', kkt_id=kkt.id)
    kkt_check_goods = check_kkt.checkkktset.all()
    context = {'kkt_check_goods': kkt_check_goods, 'check_kkt': check_kkt, 'kkt': kkt, 'form': form}
    return render(request, 'kkt_check/edit_check_kkt.html', context)


@login_required
def del_check_kkt(request, check_kkt_id):
    """Удаление чека в существующей кассе."""
    try:
        check_kkt = Check_kkt.objects.get(id=check_kkt_id)
        kkt_id = check_kkt.kkt.id
        if check_kkt.kkt.owner != request.user:
            raise Http404
        check_kkt.delete()
        return redirect('kkt_check:kkt', kkt_id=kkt_id)
    except Check_kkt.DoesNotExist:
        raise Http404


@login_required
def new_good_check_kkt(request, check_kkt_id):
    """Добавляет новую позицию в конкретный чек"""
    try:
        check_kkt = Check_kkt.objects.get(id=check_kkt_id)
    except Check_kkt.DoesNotExist:
        raise Http404
    if request.method != 'POST':
        # Данные не отправлялись; создается пустая форма.
        form = GoodForm(initial={'qty': 10000, 'tax_code': 6})
    else:
        # Отправлены данные POST; обработать данные.
        form = GoodForm(data=request.POST)
        if form.is_valid():
            new_good_check_kkt = form.save(commit=False)
            new_good_check_kkt.check_kkt = check_kkt
            new_good_check_kkt.save()
            return redirect('kkt_check:edit_check_kkt', check_kkt_id=check_kkt_id)
    # Вывести пустую или недействительную форму.
    context = {'check_kkt': check_kkt, 'form': form}
    return render(request, 'kkt_check/new_good_check_kkt.html', context)

@login_required
def edit_good_check_kkt(request, good_check_kkt_id):
    """Редактирует позицию в существующем чеке."""
    try:
        good_check_kkt = Check_good.objects.get(id=good_check_kkt_id)
    except Check_good.DoesNotExist:
        raise Http404
    check_kkt = good_check_kkt.check_kkt
    kkt = check_kkt.kkt
    if kkt.owner != request.user:
        raise Http404
    if request.method != 'POST':
        # Исходный запрос; форма заполняется данными текущей записи.
        form = GoodForm(instance=good_check_kkt)
    else:
        # Отправка данных POST; обработать данные.
        form = GoodForm(instance=good_check_kkt, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('kkt_check:edit_check_kkt', check_kkt_id=check_kkt.id)
    context = {'good_check_kkt': good_check_kkt, 'check_kkt': check_kkt, 'form': form}
    return render(request, 'kkt_check/edit_good_check_kkt.html', context)


@login_required
def del_good_check_kkt(request, good_check_kkt_id):
    """Удаление позиции в существующем чеке."""
    try:
        good_check_kkt = Check_good.objects.get(id=good_check_kkt_id)
        check_kkt_id = good_check_kkt.check_kkt.id
        if good_check_kkt.check_kkt.kkt.owner != request.user:
            raise Http404
        good_check_kkt.delete()
        return redirect('kkt_check:edit_check_kkt', check_kkt_id=check_kkt_id)
    except Check_good.DoesNotExist:
        raise Http404