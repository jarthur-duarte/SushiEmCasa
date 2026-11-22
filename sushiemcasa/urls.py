from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import cardapio, contato, pedidos, basket, checkout
from .views import admin as admin_views
from django.contrib.auth import views as auth_views
from .views import userv

app_name = 'sushiemcasa'

urlpatterns = [
     path('', cardapio.exibir_cardapio, name='cardapio'),
     path('categoria/<slug:categoria_slug>/', cardapio.exibir_cardapio, name='lista_por_categoria'),
     path('contato/', contato.pagina_contato, name='contato'),
     path('orders/', pedidos.pagina_orders, name='orders'),
     path('basket/', basket.pagina_basket, name='basket'),
     path('basket/add/<int:product_id>/', basket.add_to_cart, name='add_to_cart'),
     path('basket/update/<int:product_id>/', basket.update_cart, name='update_cart'),
     path('basket/remove/<int:product_id>/', basket.remove_from_cart, name='remove_from_cart'),
     path('basket/finalizar-whatsapp/', basket.finalizar_pedido_whatsapp, name='finalizar_whatsapp'),
     path('checkout/', checkout.pagina_checkout, name='checkout'),
     path('order/<int:order_id>/', checkout.order_detail, name='order_detail'),
     path('register/', userv.register, name='register'),
     path('login/', auth_views.LoginView.as_view(
          template_name='sushiemcasa/login.html',
          redirect_authenticated_user=True 
      ), name='login'),
     path('logout/', userv.logout_view, name='logout'),
     path('painel/', admin_views.painel_controle, name='painel_controle'),
     path('painel/deletar/<int:pk>/', admin_views.deletar_pedido, name='deletar_pedido'),
     path('painel/horarios/', admin_views.gerenciar_horarios, name='gerenciar_horarios'),
     path('gerenciar/produtos/', admin_views.GerenciarProdutosListView.as_view(), name='listar_produtos'),
     path('gerenciar/produtos/novo/', admin_views.ProdutoCreateView.as_view(), name='criar_produto'),
     path('gerenciar/produto/<int:pk>/editar/', admin_views.ProdutoUpdateView.as_view(), name='editar_produto'),
     path('gerenciar/produto/<int:pk>/excluir/', admin_views.ProdutoDeleteView.as_view(), name='excluir_produto'),
     path('gerenciar/categorias/', admin_views.CategoriaListView.as_view(), name='listar_categorias'),
     path('gerenciar/categorias/nova/', admin_views.CategoriaCreateView.as_view(), name='criar_categoria'),
     path('gerenciar/categoria/<int:pk>/editar/', admin_views.CategoriaUpdateView.as_view(), name='editar_categoria'),
     path('gerenciar/categoria/<int:pk>/excluir/', admin_views.CategoriaDeleteView.as_view(), name='excluir_categoria'),
     path('gerenciar/promocoes/', admin_views.BannerListView.as_view(), name='listar_banners'),
     path('gerenciar/promocoes/nova/', admin_views.BannerCreateView.as_view(), name='criar_banner'),
     path('gerenciar/promocao/<int:pk>/editar/', admin_views.BannerUpdateView.as_view(), name='editar_banner'),
     path('gerenciar/promocao/<int:pk>/excluir/', admin_views.BannerDeleteView.as_view(), name='excluir_banner'),
     path('gerenciar/mensagens/', admin_views.MensagemListView.as_view(), name='listar_mensagens'),
     path('gerenciar/mensagem/<int:pk>/excluir/', admin_views.MensagemDeleteView.as_view(), name='excluir_mensagem'),
     path('gerenciar/usuarios/', admin_views.UsuarioListView.as_view(), name='listar_usuarios'),
     path('gerenciar/usuario/<int:pk>/alterar/', admin_views.alterar_usuario, name='alterar_usuario'),
]
    
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)