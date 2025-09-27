from django.shortcuts import render
from sushiemcasa.models.pedidos import Order

def pagina_orders(request):
    todos_os_pedidos = Order.objects.all().order_by('-created_at')

    context = {
        'pedidos': todos_os_pedidos
    }

    return render(request, 'sushiemcasa/pedidos.html', context)