from django.shortcuts import render
from .models import Order

def home_view(request):
    # O caminho precisa ser exatamente 'usuario/pages/home.html'
    return render(request, 'usuario/pages/home.html') 

def pagina_orders(request):
    todos_os_pedidos = Order.objects.all().order_by('-created_at')

    context = {
        'pedidos': todos_os_pedidos
    }

    return render(request, 'usuario/pages/orders.html', context)