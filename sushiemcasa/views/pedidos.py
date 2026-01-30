from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from sushiemcasa.models.pedidos import Order

@login_required(login_url='/login/')
def pagina_orders(request):
    usuario = request.user
    
    if usuario.is_staff:
        todos_os_pedidos = Order.objects.all().order_by('-created_at')
    else:
        todos_os_pedidos = Order.objects.filter(user=usuario).order_by('-created_at')

    context = {
        'pedidos': todos_os_pedidos
    }
    
    return render(request, 'sushiemcasa/pedidos.html', context)