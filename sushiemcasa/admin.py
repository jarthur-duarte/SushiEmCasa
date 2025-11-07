from django.contrib import admin
# Os modelos são importados corretamente (melhor seria importar do arquivo específico)
# Vamos assumir que Produto, Order, OrderItem, Categoria estão em sushiemcasa/models/produtos.py
from .models import Produto, Order, OrderItem, Categoria
from .models.horariodefuncionamento import HorarioDeFuncionamento

# Assumindo que MensagemFeedback está em sushiemcasa/models/contato.py
# (Se MensagemFeedback estiver em .models/__init__.py, use 'from .models import MensagemFeedback')
from sushiemcasa.models.contato import MensagemFeedback 

# ----------------------------------------------------
# 1. ADMIN do CARDÁPIO
# ----------------------------------------------------

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    # 'slug' é preenchido automaticamente com base no nome
    prepopulated_fields = {'slug': ('nome',)}
    list_display = ('nome', 'slug')


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    # Adiciona a categoria como filtro e na lista de exibição
    list_display = ('nome', 'preco', 'categoria') 
    list_filter = ('categoria',)
    search_fields = ('nome', 'descricao')


# ----------------------------------------------------
# 2. ADMIN de PEDIDOS (Orders)
# ----------------------------------------------------

# INLINE: Permite ver e editar os itens do pedido dentro do formulário do Order
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    # raw_id_fields melhora o desempenho se houver muitos produtos/pedidos
    raw_id_fields = ['order', 'produto'] 
    list_display = ('produto', 'quantity', 'price') # Adicionei aqui para referência, embora não seja comum em Inlines

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at', 'total_price')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline]

# REGISTRO do Item de Pedido
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    # Adiciona 'produto' à lista para identificação clara
    list_display = ('order', 'produto', 'item_name', 'quantity', 'price')


# ----------------------------------------------------
# 3. ADMIN de CONTATO/FEEDBACK
# ----------------------------------------------------

@admin.register(MensagemFeedback)
class MensagemFeedbackAdmin(admin.ModelAdmin):

    list_display = ('nome', 'email', 'data_envio')

    list_filter = ('data_envio',)

    search_fields = ('nome', 'email', 'mensagem')
    # Campos que o administrador não deve poder editar

    readonly_fields = ('nome', 'email', 'mensagem', 'data_envio')

@admin.register(HorarioDeFuncionamento)
class HorarioDeFuncionamentoAdmin(admin.ModelAdmin):
    list_display = ('get_day_of_week_display', 'is_open', 'open_time', 'close_time')
    ordering = ('day_of_week',)