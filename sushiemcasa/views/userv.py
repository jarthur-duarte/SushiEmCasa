from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import login, logout
from sushiemcasa.forms.user import UserRegisterForm
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save() 
            login(request, user) 
            messages.success(request, f"Welcome, {user.username}! Your account has been created.")
            return redirect('sushiemcasa:cardapio') 
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegisterForm()
    
    return render(request, 'sushiemcasa/register.html', {'form': form})

@login_required(login_url='sushiemcasa:login')
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('sushiemcasa:cardapio')