from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from sushiemcasa.forms.pedidos import OrderForm
from sushiemcasa.models import Order, OrderItem, Produto # Make sure Produto is imported
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
                        'product': product, # Pass the product object itself
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
            order.user = request.user # Assign the logged-in user to the order
            order.total_price = cart_total
            order.save() # Save the order first to get an ID

            # Now create OrderItem instances linked to the saved order
            order_items_to_create = []
            for item in cart_items:
                order_items_to_create.append(
                    OrderItem(
                        order=order, # Link the item to the created order
                        produto=item['product'], # Use the product object
                        item_name=item['name'],
                        quantity=item['quantity'],
                        price=item['price'] # Use the unit price here
                    )
                )

            OrderItem.objects.bulk_create(order_items_to_create)

            # Clear the cart from the session
            request.session['cart'] = {}
            request.session.modified = True

            messages.success(request, f"Pedido #{order.id} realizado com sucesso!")
            # Redirect to the order detail page using the order's ID
            return redirect('sushiemcasa:order_detail', order_id=order.id)
        else:
            messages.error(request, "Por favor, corrija os erros abaixo.")
            print(form.errors) # Print form errors to console for debugging
    else:
        form = OrderForm()

    context = {
        'form': form,
        'cart_items': cart_items,
        'cart_total': cart_total,
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