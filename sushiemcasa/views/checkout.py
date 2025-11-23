
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from sushiemcasa.forms.pedidos import OrderForm
from sushiemcasa.models import Order, OrderItem, Produto
from decimal import Decimal
from urllib.parse import quote

def pagina_checkout(request):
    cart = request.session.get('cart', {})
    cart_items = []
    cart_total = Decimal('0.00')

    product_ids = list(cart.keys())
    if product_ids:
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

    if request.method == 'POST':
        form = OrderForm(request.POST)

        if form.is_valid():
            order = form.save(commit=False)
            
            if request.user.is_authenticated:
                order.user = request.user
            else:
                order.user = None 
            
            order.total_price = cart_total
            order.save() 

            order_items_to_create = []
            mensagem_itens_whatsapp = "" 
            
            for item in cart_items:
                order_items_to_create.append(
                    OrderItem(
                        order=order, 
                        produto=item['product'], 
                        item_name=item['name'],
                        quantity=item['quantity'],
                        price=item['price'] 
                    )
                )
                subtotal_item_wa = item['quantity'] * item['price']
                mensagem_itens_whatsapp += f"- {item['quantity']}x {item['name']} ($ {subtotal_item_wa:.2f})\n"

            OrderItem.objects.bulk_create(order_items_to_create)

            request.session['cart'] = {}
            request.session.modified = True
            
            data_hora_agendada = order.delivery_datetime.strftime("%d/%m/%Y às %H:%M")
            
            if order.user:
                nome_cliente = order.user.username
            else:
                nome_cliente = "Cliente Visitante (Não Logado)"

            numero_whatsapp_restaurante = "5587988240512"
    
            mensagem_final = (
                "🍣 *Novo Pedido - SushiEmCasa* 🍣\n\n"
                f"*Pedido ID:* #{order.id}\n"
                f"*Cliente:* {nome_cliente}\n"
                f"*Agendado para:* {data_hora_agendada}\n\n"
                "---- Itens ----\n"
                f"{mensagem_itens_whatsapp}\n"
                f"*Total do Pedido: $ {order.total_price:.2f}*\n"
            )
            
            mensagem_encodada = quote(mensagem_final)
            url_whatsapp = f"https://wa.me/{numero_whatsapp_restaurante}?text={mensagem_encodada}"

            return redirect(url_whatsapp)
        
        else:
            messages.error(request, "Por favor, corrija os erros abaixo.")
    else:
        form = OrderForm()

    context = {
        'form': form,
        'cart_items': cart_items,
        'cart_total': cart_total,
    }

    return render(request, 'sushiemcasa/checkout.html', context)

def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    context = {'order': order}
    return render(request, 'sushiemcasa/detalhe_pedidos.html', context)