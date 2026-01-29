from django.shortcuts import render, redirect
from sushiemcasa.models.pedidos import Order
from django.contrib.auth.decorators import login_required

@login_required(login_url='/usuario/login/') 
def pagina_orders(request):
    usuario = request.user
    
    if usuario.is_staff:
        todos_os_pedidos = Order.objects.all().order_by('-created_at')
    else:
        todos_os_pedidos = Order.objects.filter(costumer=usuario).order_by('-created_at')

    context = {
        'pedidos': todos_os_pedidos
    }
    
    return render(request, 'sushiemcasa/pedidos.html', context)