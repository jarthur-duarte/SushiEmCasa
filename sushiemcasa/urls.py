from django.urls import path

# IMPORTAÇÃO LIMPA: Apenas o que existe no cardapio.py
from .views.cardapio import exibir_cardapio

# Importa as views de outros módulos (mantidas)
from .views.contato import pagina_contato 
from .views.pedidos import pagina_orders 

app_name = 'sushiemcasa'

urlpatterns = [
    # 1. HOMEPAGE/CARDÁPIO (rota raiz)
    path('', exibir_cardapio, name='cardapio'),
    
    # 2. FILTRO POR CATEGORIA
    path('categoria/<slug:categoria_slug>/', exibir_cardapio, name='lista_por_categoria'), 
    
    # NOTA: ROTA DE DETALHE DO PRODUTO FOI REMOVIDA
    
    # 3. OUTRAS ROTAS
    path('contato/', pagina_contato, name='contato'),
    path('orders/', pagina_orders, name='orders'),
]