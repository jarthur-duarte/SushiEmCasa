from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import cardapio, contato, pedidos, basket, checkout

app_name = 'sushiemcasa'

urlpatterns = [
    path('', cardapio.exibir_cardapio, name='cardapio'),
    path('categoria/<slug:categoria_slug>/', cardapio.exibir_cardapio, name='lista_por_categoria'),
    path('contato/', contato.pagina_contato, name='contato'),
    path('orders/', pedidos.pagina_orders, name='orders'),

    # Cart URLs
    path('basket/', basket.pagina_basket, name='basket'),
    path('basket/add/<int:product_id>/', basket.add_to_cart, name='add_to_cart'),
    path('basket/update/<int:product_id>/', basket.update_cart, name='update_cart'),
    path('basket/remove/<int:product_id>/', basket.remove_from_cart, name='remove_from_cart'),

    # Checkout URL
    path('checkout/', checkout.pagina_checkout, name='checkout'),
    path('order/<int:order_id>/', checkout.order_detail, name='order_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
