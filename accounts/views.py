from django.shortcuts import redirect, render

from .forms import CreateUserForm
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .decorators import unauthenticated_user
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User



@unauthenticated_user
def RegisterPage(request):
    form = CreateUserForm()
    
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # delay saving to set is_active
            user.is_active = False          # user must be approved by admin
            user.save()

            username = form.cleaned_data.get('username')
            messages.success(request, f'Account was created for {username}. Please wait for admin approval.')
            return redirect('login')

    context = {'form': form}
    return render(request, 'accounts/register.html', context)


@unauthenticated_user
def LoginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
            if check_password(password, user.password):
                if user.is_active:
                    login(request, user)
                    return redirect('vectorizer_ui')
                else:
                    messages.error(request, 'Your account is pending admin approval.')
            else:
                messages.error(request, 'Username or password is incorrect.')
        except User.DoesNotExist:
            messages.error(request, 'Username or password is incorrect.')

    return render(request, 'accounts/login.html')


def LogoutUser(request):
    logout(request)
    return redirect('login')

