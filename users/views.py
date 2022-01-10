from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .forms import UserForm, UserForm, ProfileEditForm
from .models import Profile
from django.contrib.auth.decorators import login_required




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
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('kkt_check:kktlist')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(request,
                      'users/edit.html',
                      {'profile_form': profile_form, 'user_form': user_form})


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
