# sushiemcasa/views/basket.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from sushiemcasa.models import Produto
from decimal import Decimal

def pagina_basket(request):
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
                        'name': product.nome,
                        'price': product.preco,
                        'quantity': quantity,
                        'total': total_item_price,
                        'image_url': product.imagem.url if product.imagem else None # Add image URL
                    })
                    cart_total += total_item_price

    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
    }
    return render(request, 'sushiemcasa/basket.html', context)

@require_POST
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id) # Ensure product_id is a string key
    quantity = int(request.POST.get('quantity', 1))

    # Optional: Check if product exists before adding
    try:
        product = Produto.objects.get(id=product_id)
    except Produto.DoesNotExist:
        # Handle the case where the product doesn't exist (e.g., show an error)
        # For simplicity, we'll just ignore it here, but you might want better handling
        return redirect('sushiemcasa:cardapio') # Redirect back to menu

    if product_id_str in cart:
        cart[product_id_str]['quantity'] += quantity
    else:
        cart[product_id_str] = {'quantity': quantity}

    request.session['cart'] = cart
    request.session.modified = True # Ensure session is saved

    # Redirect back to the page the user was on, or to the basket
    # For simplicity, let's always redirect to the basket page after adding
    return redirect('sushiemcasa:basket')

@require_POST
def update_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    new_quantity = int(request.POST.get('quantity', 0))

    if product_id_str in cart:
        if new_quantity > 0:
            cart[product_id_str]['quantity'] = new_quantity
        else:
            # Remove item if quantity is set to 0 or less
            del cart[product_id_str]

    request.session['cart'] = cart
    request.session.modified = True
    return redirect('sushiemcasa:basket')

@require_POST
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]

    request.session['cart'] = cart
    request.session.modified = True
    return redirect('sushiemcasa:basket')