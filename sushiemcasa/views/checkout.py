from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.db import transaction
from django.http import Http404
from django.urls import reverse
from django.utils import timezone
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
            order_items = []
            itens_whatsapp = ""
            BULLET = "▪"

            # Pedido e itens são gravados juntos: se algo falhar, nada fica salvo
            # e o carrinho do cliente continua intacto.
            with transaction.atomic():
                order.save()
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

            nome_cliente = (
                request.user.username
                if request.user.is_authenticated
                else "Guest customer"
            )

            data_agendada = timezone.localtime(order.delivery_datetime).strftime("%m/%d/%Y at %I:%M %p")
            request.session['cart'] = {}
            request.session.modified = True

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
    # Só o dono do pedido e a equipe da loja podem ver os detalhes.
    if not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path(), reverse('sushiemcasa:login'))
    order = get_object_or_404(Order, id=order_id)
    if not request.user.is_staff and order.user_id != request.user.id:
        raise Http404("Order not found.")
    return render(
        request,
        'sushiemcasa/detalhe_pedidos.html',
        {'order': order}
    )
