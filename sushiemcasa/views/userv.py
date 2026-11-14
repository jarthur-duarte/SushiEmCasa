from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import login, logout
from sushiemcasa.forms.user import UserRegisterForm
from django.contrib.auth.decorators import login_required
from django.utils.http import url_has_allowed_host_and_scheme


def _proximo_seguro(request):
    """Página para onde voltar depois do cadastro (ex.: o checkout), só se for deste site."""
    destino = request.POST.get('next') or request.GET.get('next') or ''
    if destino and url_has_allowed_host_and_scheme(destino, allowed_hosts={request.get_host()},
                                                   require_https=request.is_secure()):
        return destino
    return ''

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save() 
            login(request, user) 
            messages.success(request, f"Welcome, {user.username}! Your account has been created.")
            return redirect(_proximo_seguro(request) or 'sushiemcasa:cardapio')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegisterForm()
    
    return render(request, 'sushiemcasa/register.html', {'form': form, 'next': _proximo_seguro(request)})

@login_required(login_url='sushiemcasa:login')
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('sushiemcasa:cardapio')