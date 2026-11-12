from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from decimal import Decimal
from urllib.parse import quote_plus

from sushiemcasa.forms.pedidos import OrderForm
from sushiemcasa.models import Order, OrderItem, Produto


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
            quantity = item_data.get('quantity', 0)

            if product and quantity > 0:
                total_item_price = product.preco * quantity

                cart_items.append({
                    'product': product,
                    'name': product.nome,
                    'price': product.preco,
                    'quantity': quantity,
                    'total': total_item_price,
                    'image_url': product.imagem.url if product.imagem else None
                })

                cart_total += total_item_price

    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect('sushiemcasa:basket')
    if request.method == 'POST':
        form = OrderForm(request.POST)

        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user if request.user.is_authenticated else None
            order.total_price = cart_total
            order.save()
            order_items = []
            itens_whatsapp = ""
            BULLET = "▪"

            for item in cart_items:
                order_items.append(
                    OrderItem(
                        order=order,
                        produto=item['product'],
                        item_name=item['name'],
                        quantity=item['quantity'],
                        price=item['price']
                    )
                )

                subtotal = item['quantity'] * item['price']
                itens_whatsapp += (
                    f"{BULLET} {item['quantity']}x {item['name']} "
                    f"($ {subtotal:.2f})\n"
                )
            OrderItem.objects.bulk_create(order_items)
            request.session['cart'] = {}
            request.session.modified = True
            nome_cliente = (
                request.user.username
                if request.user.is_authenticated
                else "Guest customer"
            )

            data_agendada = order.delivery_datetime.strftime("%m/%d/%Y at %I:%M %p")

            mensagem = (
                f"🍣 NEW ORDER - SUSHI EM CASA\n\n"
                f"📄 Order #: {order.id}\n"
                f"👤 Customer: {nome_cliente}\n"
                f"📅 Scheduled for: {data_agendada}\n\n"
                f"🛒 ORDER ITEMS\n"
                f"{itens_whatsapp}\n"
                f"💰 ORDER TOTAL: $ {order.total_price:.2f}"
            )
            numero_whatsapp = "12397719811"

            mensagem_codificada = quote_plus(
                mensagem,
                encoding="utf-8"
            )

            url_whatsapp = (
                "https://api.whatsapp.com/send"
                f"?phone={numero_whatsapp}"
                f"&text={mensagem_codificada}"
            )

            return redirect(url_whatsapp)

        else:
            messages.error(request, "Please correct the errors below.")

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
    return render(
        request,
        'sushiemcasa/detalhe_pedidos.html',
        {'order': order}
    )
