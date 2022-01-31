from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .forms import UserForm, UserForm, ProfileEditForm
from .models import Profile
from partners.models import Partnerprofile
from partners.forms import PartnerProfileEditForm
from django.contrib.auth.decorators import login_required
from icecream import ic




def register(request):
    """Регистрирует нового пользователя."""
    if request.method != 'POST':
        # Выводит пустую форму регистрации.
        form = UserForm(request.POST)
    else:
        # Обработка заполненной формы.
        form = UserForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            profile = Profile.objects.create(user=new_user)
            # Выполнение входа и перенаправление на домашнюю страницу.
            login(request, new_user)
            return redirect('kkt_check:index')
    # Вывести пустую или недействительную форму.
    context = {'form': form}
    return render(request, 'users/register.html', context)


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)
        # Сохраняем текущий статус клиента
        current_client_satus = request.user.profile.client_status
        if current_client_satus == 1:
            partner_profile_form = PartnerProfileEditForm(instance=request.user.partnerprofile, data=request.POST)
            if partner_profile_form.is_valid():
                partner_profile_form.save()
        if user_form.is_valid() and profile_form.is_valid():
            new_profile = profile_form.save(commit=False)
            # Если статус сменился клиент на партнер, то создаем партнерский профиль
            if current_client_satus == 0 and new_profile.client_status == 1:
                partnerprofile = Partnerprofile.objects.create(user=request.user)
            # Если клиент уже имеет статус партнера, то не меняем
            if current_client_satus == 1 and new_profile.client_status == 0:
                new_profile.client_status = 1
            new_profile.save()
            user_form.save()

            return redirect('kkt_check:kktlist')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
        if request.user.profile.client_status == 1:
            partner_profile_form = PartnerProfileEditForm(instance=request.user.partnerprofile)
            return render(request,
                          'users/edit.html',
                          {'profile_form': profile_form,
                           'user_form': user_form,
                           'partner_profile_form': partner_profile_form})
    return render(request, 'users/edit.html', {'profile_form': profile_form, 'user_form': user_form})


def register_old(request):
    """Регистрирует нового пользователя."""
    if request.method != 'POST':
        # Выводит пустую форму регистрации.
        form = UserCreationForm()
    else:
        # Обработка заполненной формы.
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            new_user = form.save()
            # Выполнение входа и перенаправление на домашнюю страницу.
            login(request, new_user)
            return redirect('kkt_check:index')
    # Вывести пустую или недействительную форму.
    context = {'form': form}
    return render(request, 'users/register.html', context)
