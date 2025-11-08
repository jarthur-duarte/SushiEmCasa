# sushiemcasa/views/checkout.py (ATUALIZADO PARA WHATSAPP)

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from sushiemcasa.forms.pedidos import OrderForm
from sushiemcasa.models import Order, OrderItem, Produto, HorarioDeFuncionamento
from decimal import Decimal
from urllib.parse import quote # 👈 ADICIONADO

def pagina_checkout(request):
    cart = request.session.get('cart', {})
    cart_items = []
    cart_total = Decimal('0.00')

    product_ids = list(cart.keys())
    if product_ids:
        # ... (lógica para pegar os 'cart_items' - igual a antes) ...
        products = Produto.objects.filter(id__in=product_ids)
        product_map = {str(product.id): product for product in products}

        for product_id, item_data in cart.items():
            product = product_map.get(product_id)
            if product:
                quantity = item_data.get('quantity', 0)
                if quantity > 0:
                    total_item_price = product.preco * quantity
                    cart_items.append({
                        'product_id': product_id,
                        'product': product, 
                        'name': product.nome,
                        'price': product.preco,
                        'quantity': quantity,
                        'total': total_item_price,
                        'image_url': product.imagem.url if product.imagem else None
                    })
                    cart_total += total_item_price

    if not cart_items:
        messages.error(request, "Seu carrinho está vazio.")
        return redirect('sushiemcasa:basket')

    # --- LÓGICA DE VERIFICAÇÃO DE HORÁRIO (para agendamento) ---
    # (Removido o 'is_open' que bloqueava o POST)
    
    if request.method == 'POST':
        form = OrderForm(request.POST)

        # (Removemos o bloqueio de POST se a loja estivesse fechada)

        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user 
            order.total_price = cart_total
            order.save() # <-- Pedido salvo no banco!

            order_items_to_create = []
            mensagem_itens_whatsapp = "" # String para a mensagem do WhatsApp
            
            for item in cart_items:
                # Cria os itens para salvar no banco
                order_items_to_create.append(
                    OrderItem(
                        order=order, 
                        produto=item['product'], 
                        item_name=item['name'],
                        quantity=item['quantity'],
                        price=item['price'] 
                    )
                )
                # Cria os itens para a mensagem
                subtotal_item_wa = item['quantity'] * item['price']
                mensagem_itens_whatsapp += f"- {item['quantity']}x {item['name']} ($ {subtotal_item_wa:.2f})\n"


            OrderItem.objects.bulk_create(order_items_to_create)

            request.session['cart'] = {}
            request.session.modified = True
            
            # -----------------------------------------------------------------
            # 👇 NOVA LÓGICA DO WHATSAPP ADICIONADA AQUI 👇
            # -----------------------------------------------------------------
            
            # Pega a data/hora agendada que o usuário escolheu
            data_hora_agendada = order.delivery_datetime.strftime("%d/%m/%Y às %H:%M")

            numero_whatsapp_restaurante = "87988240512" # (Pode mudar se precisar)
    
            mensagem_final = (
                " *Novo Pedido Agendado - SushiEmCasa* \n\n"
                f"*Pedido ID:* #{order.id}\n"
                f"*Cliente:* {order.user.username}\n"
                f"*Agendado para:* {data_hora_agendada}\n\n"
                "---- Itens ----\n"
                f"{mensagem_itens_whatsapp}\n"
                f"*Total do Pedido: $ {order.total_price:.2f}*\n"
            )
            
            mensagem_encodada = quote(mensagem_final)
            url_whatsapp = f"https://wa.me/{numero_whatsapp_restaurante}?text={mensagem_encodada}"

            # Em vez de ir para a página de detalhe,
            # redireciona para o WhatsApp
            return redirect(url_whatsapp)
        
        else:
            messages.error(request, "Por favor, corrija os erros abaixo.")
            print(form.errors)
    else:
        form = OrderForm()

    context = {
        'form': form,
        'cart_items': cart_items,
        'cart_total': cart_total,
        # 'is_store_open': is_open (removido para não conflitar com agendamento)
    }

    return render(request, 'sushiemcasa/checkout.html', context)


# (A view 'order_detail' continua igual)
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    context = {'order': order}
    return render(request, 'sushiemcasa/detalhe_pedidos.html', context)