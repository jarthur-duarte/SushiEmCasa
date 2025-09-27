# sushiemcasa/urls.py  <-- NOVO ARQUIVO

from django.urls import path
from . import views  # Importa as views do app sushiemcasa

app_name = 'sushiemcasa'
urlpatterns = [
    # A URL que você perguntou vai aqui
    path('', views.homepage, name='homepage'),
    #path('contato/', views.pagina_de_contato, name='contato'),

    # Você pode adicionar outras URLs deste app aqui no futuro
    # path('cardapio/', views.mostrar_cardapio, name='cardapio'),
    # path('pedidos/', views.listar_pedidos, name='pedidos'),
]