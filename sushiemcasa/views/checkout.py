from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from sushiemcasa.forms.pedidos import OrderForm
from sushiemcasa.models import Order, OrderItem, Produto

def pagina_checkout(request):
    cart = request.session.get('cart', {})
    
    #if not cart:
        #messages.error(request, "Seu carrinho está vazio.")
        #return redirect('sushiemcasa:cardapio') 

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            
            #if request.user.is_authenticated:
                #.user = request.user
            #else:
                #.error(request, "Você precisa estar logado para finalizar o pedido.")
                #return redirect('login_url')

            total_price = 0
            order_items_to_create = []
            
            from sushiemcasa.models import Produto
            
            for product_id, item_data in cart.items():
                try:
                    product = Produto.objects.get(id=product_id)
                    quantity = item_data.get('quantity', 0)
                    if quantity > 0:
                        price = product.preco * quantity
                        total_price += price
                        order_items_to_create.append(
                            OrderItem(
                                product=product, 
                                item_name=product.nome, 
                                quantity=quantity,
                                price=price
                            )
                        )
                except Produto.DoesNotExist:
                    messages.error(request, f"Produto com ID {product_id} não encontrado.")
                    return render(request, 'sushiemcasa/checkout.html', {'form': form, 'cart': cart})

            if not order_items_to_create:
                 messages.error(request, "Seu carrinho está vazio ou contém itens inválidos.")
                 return redirect('sushiemcasa:basket')

            order.total_price = total_price
            order.save()

            for item in order_items_to_create:
                item.order = order
            OrderItem.objects.bulk_create(order_items_to_create)

            request.session['cart'] = {}
            
            messages.success(request, f"Pedido #{order.id} realizado com sucesso!")
            return redirect('sushiemcasa:order_detail', order_id=order.id) 
            
        else:
            messages.error(request, "Por favor, corrija os erros abaixo.")
            
    else:
        form = OrderForm()

    context = {
        'form': form,
        'cart_items': [],
        'cart_total': 0
    }
    
    total = 0
    items_list = []
    from sushiemcasa.models import Produto
    for product_id, item_data in cart.items():
         try:
            product = Produto.objects.get(id=product_id)
            quantity = item_data.get('quantity', 1) 
            item_total = product.preco * quantity
            items_list.append({'product': product, 'quantity': quantity, 'total': item_total})
            total += item_total
         except Produto.DoesNotExist:
             pass
    
    context['cart_items'] = items_list
    context['cart_total'] = total

    return render(request, 'sushiemcasa/checkout.html', context)

def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {'order': order}
    return render(request, 'sushiemcasa/templates/sushiemcasa/detalhe_pedidos.html', context)