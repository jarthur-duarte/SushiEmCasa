"""
Testes unitários (sem navegador) para rodar no CI com `python manage.py test`.

Cobrem os modelos, a validação do formulário de pedido e as views de
cardápio, carrinho e checkout usando o Django test client — sem depender
de Selenium/Chrome, o que os torna rápidos e adequados para o pipeline.
"""
import datetime
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

from sushiemcasa.models import (
    Categoria,
    Produto,
    Order,
    OrderItem,
    HorarioDeFuncionamento,
    MensagemFeedback,
)
from sushiemcasa.forms.pedidos import OrderForm

User = get_user_model()


def _horario_para_todos_os_dias(is_open, open_time=None, close_time=None):
    """Cria/atualiza a configuração de horário dos 7 dias da semana."""
    HorarioDeFuncionamento.objects.all().delete()
    for day in range(7):
        HorarioDeFuncionamento.objects.create(
            day_of_week=day,
            is_open=is_open,
            open_time=open_time,
            close_time=close_time,
        )


# =========================================================================
# MODELOS
# =========================================================================
class CategoriaProdutoModelTests(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nome='Temaki', slug='temaki')
        self.produto = Produto.objects.create(
            nome='Temaki Salmão',
            descricao='Delicioso',
            preco=Decimal('25.00'),
            categoria=self.categoria,
            imagem='',
        )

    def test_categoria_str(self):
        self.assertEqual(str(self.categoria), 'Temaki')

    def test_produto_str_inclui_categoria(self):
        self.assertEqual(str(self.produto), 'Temaki Salmão (Temaki)')


class HorarioDeFuncionamentoModelTests(TestCase):
    def test_str_dia_fechado(self):
        horario = HorarioDeFuncionamento(day_of_week=0, is_open=False)
        self.assertIn('Fechado', str(horario))

    def test_str_dia_aberto_com_horarios(self):
        horario = HorarioDeFuncionamento(
            day_of_week=0,
            is_open=True,
            open_time=datetime.time(9, 0),
            close_time=datetime.time(18, 0),
        )
        self.assertEqual(str(horario), 'Segunda-feira: 09:00 - 18:00')

    def test_clean_aberto_sem_horarios_levanta_erro(self):
        horario = HorarioDeFuncionamento(day_of_week=1, is_open=True)
        with self.assertRaises(ValidationError):
            horario.clean()

    def test_clean_fechamento_antes_da_abertura_levanta_erro(self):
        horario = HorarioDeFuncionamento(
            day_of_week=1,
            is_open=True,
            open_time=datetime.time(18, 0),
            close_time=datetime.time(16, 0),
        )
        with self.assertRaises(ValidationError):
            horario.clean()

    def test_clean_dia_fechado_limpa_horarios(self):
        horario = HorarioDeFuncionamento(
            day_of_week=1,
            is_open=False,
            open_time=datetime.time(9, 0),
            close_time=datetime.time(18, 0),
        )
        horario.clean()
        self.assertIsNone(horario.open_time)
        self.assertIsNone(horario.close_time)


class OrderModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joao', password='x')

    def test_order_str(self):
        order = Order.objects.create(user=self.user, total_price=Decimal('10.00'))
        self.assertEqual(str(order), f'Order #{order.id} - joao')

    def test_clean_entrega_antes_de_24h_levanta_erro(self):
        order = Order(
            user=self.user,
            total_price=Decimal('10.00'),
            delivery_datetime=timezone.now() + datetime.timedelta(hours=2),
        )
        with self.assertRaises(ValidationError):
            order.clean()

    def test_clean_entrega_com_mais_de_24h_ok(self):
        order = Order(
            user=self.user,
            total_price=Decimal('10.00'),
            delivery_datetime=timezone.now() + datetime.timedelta(hours=30),
        )
        # Não deve levantar exceção
        order.clean()

    def test_order_item_str(self):
        order = Order.objects.create(user=self.user, total_price=Decimal('10.00'))
        categoria = Categoria.objects.create(nome='Combo', slug='combo')
        produto = Produto.objects.create(
            nome='Combo 1', descricao='d', preco=Decimal('5.00'),
            categoria=categoria, imagem='',
        )
        item = OrderItem.objects.create(
            order=order, produto=produto, item_name='Combo 1',
            quantity=2, price=Decimal('5.00'),
        )
        self.assertEqual(str(item), f'2x Combo 1 (Order #{order.id})')


class MensagemFeedbackModelTests(TestCase):
    def test_str_com_nome(self):
        msg = MensagemFeedback(nome='Ana', mensagem='Oi')
        self.assertEqual(str(msg), 'Mensagem de Ana')

    def test_str_anonimo(self):
        msg = MensagemFeedback(mensagem='Oi')
        self.assertEqual(str(msg), 'Mensagem de Anônimo')


# =========================================================================
# FORMULÁRIO DE PEDIDO
# =========================================================================
class OrderFormTests(TestCase):
    def _proxima_data_valida(self):
        """Retorna um datetime > 24h no futuro, dia útil, dentro de 10h-20h."""
        dt = timezone.localtime(timezone.now()) + datetime.timedelta(days=2)
        dt = dt.replace(hour=14, minute=0, second=0, microsecond=0)
        while dt.weekday() == 6:  # pula domingo
            dt += datetime.timedelta(days=1)
        return dt

    def test_data_valida_passa(self):
        form = OrderForm(data={'delivery_datetime': self._proxima_data_valida()})
        self.assertTrue(form.is_valid(), form.errors)

    def test_menos_de_24h_invalido(self):
        dt = timezone.localtime(timezone.now()) + datetime.timedelta(hours=2)
        form = OrderForm(data={'delivery_datetime': dt})
        self.assertFalse(form.is_valid())

    def test_domingo_invalido(self):
        dt = self._proxima_data_valida()
        while dt.weekday() != 6:  # avança até um domingo
            dt += datetime.timedelta(days=1)
        form = OrderForm(data={'delivery_datetime': dt})
        self.assertFalse(form.is_valid())

    def test_fora_do_horario_invalido(self):
        dt = self._proxima_data_valida().replace(hour=22)
        form = OrderForm(data={'delivery_datetime': dt})
        self.assertFalse(form.is_valid())


# =========================================================================
# VIEWS DO CARRINHO
# =========================================================================
class BasketViewTests(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nome='Sushi', slug='sushi')
        self.produto = Produto.objects.create(
            nome='Nigiri', descricao='d', preco=Decimal('12.00'),
            categoria=self.categoria, imagem='',
        )

    def test_add_to_cart_coloca_item_na_sessao(self):
        response = self.client.post(
            reverse('sushiemcasa:add_to_cart', args=[self.produto.id]),
            {'quantity': 2},
        )
        self.assertRedirects(response, reverse('sushiemcasa:basket'))
        cart = self.client.session['cart']
        self.assertEqual(cart[str(self.produto.id)]['quantity'], 2)

    def test_add_to_cart_produto_inexistente_redireciona_cardapio(self):
        response = self.client.post(
            reverse('sushiemcasa:add_to_cart', args=[9999]),
            {'quantity': 1},
        )
        self.assertRedirects(response, reverse('sushiemcasa:cardapio'))

    def test_update_cart_altera_quantidade(self):
        self.client.post(
            reverse('sushiemcasa:add_to_cart', args=[self.produto.id]),
            {'quantity': 1},
        )
        self.client.post(
            reverse('sushiemcasa:update_cart', args=[self.produto.id]),
            {'quantity': 5},
        )
        self.assertEqual(
            self.client.session['cart'][str(self.produto.id)]['quantity'], 5
        )

    def test_update_cart_quantidade_zero_remove_item(self):
        self.client.post(
            reverse('sushiemcasa:add_to_cart', args=[self.produto.id]),
            {'quantity': 1},
        )
        self.client.post(
            reverse('sushiemcasa:update_cart', args=[self.produto.id]),
            {'quantity': 0},
        )
        self.assertNotIn(str(self.produto.id), self.client.session['cart'])

    def test_remove_from_cart(self):
        self.client.post(
            reverse('sushiemcasa:add_to_cart', args=[self.produto.id]),
            {'quantity': 1},
        )
        self.client.post(
            reverse('sushiemcasa:remove_from_cart', args=[self.produto.id]),
        )
        self.assertNotIn(str(self.produto.id), self.client.session['cart'])

    def test_pagina_basket_mostra_total(self):
        self.client.post(
            reverse('sushiemcasa:add_to_cart', args=[self.produto.id]),
            {'quantity': 3},
        )
        response = self.client.get(reverse('sushiemcasa:basket'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cart_total'], Decimal('36.00'))


# =========================================================================
# VIEW DO CARDÁPIO (mensagem de loja aberta/fechada)
# =========================================================================
class CardapioViewTests(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nome='Sushi', slug='sushi')
        Produto.objects.create(
            nome='Nigiri', descricao='d', preco=Decimal('12.00'),
            categoria=self.categoria, imagem='',
        )

    def test_loja_fechada_mostra_aviso(self):
        _horario_para_todos_os_dias(is_open=False)
        response = self.client.get(reverse('sushiemcasa:cardapio'))
        mensagens = [m.message for m in get_messages(response.wsgi_request)]
        self.assertTrue(
            any('loja fechada' in m.lower() for m in mensagens),
            f'Esperava aviso de loja fechada, veio: {mensagens}',
        )

    def test_loja_aberta_nao_mostra_aviso(self):
        _horario_para_todos_os_dias(
            is_open=True,
            open_time=datetime.time(0, 0),
            close_time=datetime.time(23, 59),
        )
        response = self.client.get(reverse('sushiemcasa:cardapio'))
        mensagens = [m.message for m in get_messages(response.wsgi_request)]
        self.assertFalse(
            any('loja fechada' in m.lower() for m in mensagens),
            f'Não esperava aviso de loja fechada, veio: {mensagens}',
        )


# =========================================================================
# VIEW DE CHECKOUT
# =========================================================================
class CheckoutViewTests(TestCase):
    def test_carrinho_vazio_redireciona_para_basket(self):
        response = self.client.get(reverse('sushiemcasa:checkout'))
        self.assertRedirects(response, reverse('sushiemcasa:basket'))
