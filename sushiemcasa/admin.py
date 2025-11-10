from django.contrib import admin
from .models.produtos import Produto, Categoria
from .models.pedidos import Order, OrderItem
from .models.horariodefuncionamento import HorarioDeFuncionamento
from .models.contato import MensagemFeedback

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('nome',)}
    list_display = ('nome', 'slug')


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco', 'categoria', 'disponivel')
    list_filter = ('categoria', 'disponivel')
    search_fields = ('nome', 'descricao')
    
    list_editable = ('preco', 'categoria', 'disponivel')
    ordering = ('nome',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['produto']
    readonly_fields = ('item_name', 'price')
    extra = 0 

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'delivery_datetime', 'created_at', 'total_price')
    list_filter = ('status', 'delivery_datetime', 'created_at')
    inlines = [OrderItemInline]
    ordering = ('-created_at',) 
    
    search_fields = ('id', 'user__username', 'user__email')
    
    readonly_fields = ('user', 'total_price', 'created_at', 'delivery_datetime')



@admin.register(MensagemFeedback)
class MensagemFeedbackAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'data_envio')
    list_filter = ('data_envio',)
    search_fields = ('nome', 'email', 'mensagem')
    readonly_fields = ('nome', 'email', 'mensagem', 'data_envio')

@admin.register(HorarioDeFuncionamento)
class HorarioDeFuncionamentoAdmin(admin.ModelAdmin):
    list_display = ('get_day_of_week_display', 'is_open', 'open_time', 'close_time')
    ordering = ('day_of_week',)
    list_editable = ('is_open', 'open_time', 'close_time')