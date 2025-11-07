from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from sushiemcasa.forms.pedidos import OrderForm
from sushiemcasa.models import Order, OrderItem, Produto, HorarioDeFuncionamento # Make sure Produto is imported
from decimal import Decimal

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

    # --- 2. ADIÇÃO DA LÓGICA DE VERIFICAÇÃO DE HORÁRIO ---
    now = timezone.localtime(timezone.now())
    current_day_int = now.weekday() # Segunda=0, Domingo=6
    current_time = now.time()
    
    is_open = False # Começa como fechado
    
    try:
        today_schedule = HorarioDeFuncionamento.objects.get(day_of_week=current_day_int)
        
        if (today_schedule.is_open and 
            today_schedule.open_time and 
            today_schedule.close_time and
            today_schedule.open_time <= current_time < today_schedule.close_time):
            
            is_open = True
            
    except HorarioDeFuncionamento.DoesNotExist:
        is_open = False # Se não houver configuração, consideramos fechado
    # --- FIM DA LÓGICA DE VERIFICAÇÃO ---

    if request.method == 'POST':
        form = OrderForm(request.POST)

        # --- 3. ADIÇÃO DO BLOQUEIO DE POST ---
        # Verifica DE NOVO se a loja está aberta ANTES de validar o form
        if not is_open:
            messages.error(request, "Desculpe, a loja fechou enquanto você finalizava o pedido. Tente novamente mais tarde.")
            # Re-renderiza a página (não redireciona) para mostrar o erro
            context = {
                'form': form,
                'cart_items': cart_items,
                'cart_total': cart_total,
                'is_store_open': is_open # Passa o status de fechado
            }
            return render(request, 'sushiemcasa/checkout.html', context)
        # --- FIM DO BLOQUEIO ---

        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user 
            order.total_price = cart_total
            order.save() 

            order_items_to_create = []
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

            OrderItem.objects.bulk_create(order_items_to_create)

            request.session['cart'] = {}
            request.session.modified = True

            messages.success(request, f"Pedido #{order.id} realizado com sucesso!")
            return redirect('sushiemcasa:order_detail', order_id=order.id)
        else:
            messages.error(request, "Por favor, corrija os erros abaixo.")
            print(form.errors)
    else:
        form = OrderForm()

    context = {
        'form': form,
        'cart_items': cart_items,
        'cart_total': cart_total,
        'is_store_open': is_open # <-- 4. PASSA A VARIÁVEL PARA O CONTEXTO
    }

    return render(request, 'sushiemcasa/checkout.html', context)

# View to display a specific order
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    # Optional: Add security check if needed (e.g., ensure the user viewing the order is the owner)
    # if order.user != request.user and not request.user.is_staff:
    #     return HttpResponseForbidden("You are not allowed to view this order.")

    context = {'order': order}
    return render(request, 'sushiemcasa/detalhe_pedidos.html', context)