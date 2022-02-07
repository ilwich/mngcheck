from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, Http404
from .forms import EditPassword, UserForm, ProfileEditForm, RegisterForm
from .models import Profile
from partners.models import Partnerprofile
from partners.forms import PartnerProfileEditForm
from django.contrib.auth.decorators import login_required
from mngcheck.settings import DEFAULT_FROM_EMAIL
from icecream import ic


def send_new_partner_msg(user):
    """Отправка сообщения дилеру,что добавлен новый партнер"""
    subject = f'Добавлен новый партнер {user.profile.legal_entity}'
    message = f'Новый партнер с ИНН {user.partnerprofile.inn} неоходимо добавить в учетную систему.'
    # формирования списка электронных адресов дилеров
    try:
        dilers = Profile.objects.filter(client_status=2)
    except:
        return HttpResponse('Не найден адрес дилера')
    diler_email = []
    for diler in dilers:
        diler_email.append(diler.user.email)
    # Отправка сообщений делерамм
    try:
        send_mail(subject, message,
                  DEFAULT_FROM_EMAIL, diler_email)
    except BadHeaderError:
        return HttpResponse('Ошибка в теме письма.')


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserForm(instance=request.user, data=request.POST)
        try:
            profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)
        except Partnerprofile.DoesNotExist:
            raise Http404
        # Сохраняем текущий статус клиента
        current_client_satus = request.user.profile.client_status
        # Отслеживаем состояние отправки сообщения о новом партнёре
        send_mail_of_new_partner = False
        if current_client_satus == 1:
            partner_profile_form = PartnerProfileEditForm(instance=request.user.partnerprofile, data=request.POST)
            if partner_profile_form.is_valid():
                partner_profile_form.save()
        if user_form.is_valid() and profile_form.is_valid():
            new_profile = profile_form.save(commit=False)
            # Если статус сменился клиент на партнер, то создаем партнерский профиль
            if current_client_satus == 0 and new_profile.client_status == 1:
                partnerprofile = Partnerprofile.objects.create(user=request.user)
                send_mail_of_new_partner = True
            # Если клиент уже имеет статус партнера, то не меняем
            if current_client_satus == 1 and new_profile.client_status == 0:
                new_profile.client_status = 1
            new_profile.save()
            user_form.save()
            # отправка оповещения делеру о создании нового партнёра
            if send_mail_of_new_partner:
                send_new_partner_msg(user=request.user)
            return redirect('kkt_check:kktlist')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

        if request.user.profile.client_status >= 1:
            partner_profile_form = PartnerProfileEditForm(instance=request.user.partnerprofile)
        else:
            partner_profile_form = PartnerProfileEditForm()
    return render(request,
                  'users/edit.html',
                  {'profile_form': profile_form,
                   'user_form': user_form,
                   'partner_profile_form': partner_profile_form})


def register(request):
    """Регистрирует нового пользователя."""
    if request.method != 'POST':
        # Выводит пустую форму регистрации.
        form = RegisterForm()
    else:
        # Обработка заполненной формы.
        form = RegisterForm(data=request.POST)
        if form.is_valid():
            new_user = form.save()
            # Создание дополнительного профиля пользователя
            profile = Profile.objects.create(user=new_user)
            # Выполнение входа и перенаправление на домашнюю страницу.

            login(request, new_user)
            return redirect('users:edit')
    # Вывести пустую или недействительную форму.
    context = {'form': form}
    return render(request, 'users/register.html', context)
