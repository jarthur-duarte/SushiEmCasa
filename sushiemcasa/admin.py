from django.contrib import admin

# Register your models here.
from    .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['order']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at', 'total_price')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'item_name', 'quantity', 'price')




from django.contrib import admin
from sushiemcasa.models.contato import MensagemFeedback

@admin.register(MensagemFeedback)
class MensagemFeedbackAdmin(admin.ModelAdmin):
    
    # Colunas que serão exibidas na lista de feedbacks
    list_display = ('nome', 'email', 'data_envio')

    # Adiciona um filtro na lateral direita por data
    list_filter = ('data_envio',)

    # Adiciona uma barra de busca que procura nestes campos
    search_fields = ('nome', 'email', 'mensagem')
    
    # Faz com que os campos não sejam editáveis no admin
    # (geralmente não queremos editar o feedback de um usuário)
    readonly_fields = ('nome', 'email', 'mensagem', 'data_envio')
