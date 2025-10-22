from django.urls import path
from .views.cardapio import exibir_cardapio
from .views.contato import pagina_contato
from .views.pedidos import pagina_orders
from .views.basket import pagina_basket 
from .views.checkout import pagina_checkout, order_detail

app_name = 'sushiemcasa'

urlpatterns = [
    path('', exibir_cardapio, name='cardapio'),  # rota raiz
    path('categoria/<slug:categoria_slug>/', exibir_cardapio, name='lista_por_categoria'),
    path('contato/', pagina_contato, name='contato'),
    path('orders/', pagina_orders, name='orders'),
    path('basket/',pagina_basket,name='basket'),
    path('checkout/', pagina_checkout, name='checkout'), 
    path('order/<int:order_id>/', order_detail, name='detalhe_pedidos'),
]
