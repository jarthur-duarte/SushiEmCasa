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
        self.assertIn('Closed', str(horario))

    def test_str_dia_aberto_com_horarios(self):
        horario = HorarioDeFuncionamento(
            day_of_week=0,
            is_open=True,
            open_time=datetime.time(9, 0),
            close_time=datetime.time(18, 0),
        )
        self.assertEqual(str(horario), 'Monday: 09:00 - 18:00')

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
        self.assertEqual(str(msg), 'Message from Ana')

    def test_str_anonimo(self):
        msg = MensagemFeedback(mensagem='Oi')
        self.assertEqual(str(msg), 'Message from Anonymous')


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
# VIEW DO CARDÁPIO (status de loja aberta/fechada no contexto)
# =========================================================================
class CardapioViewTests(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nome='Sushi', slug='sushi')
        Produto.objects.create(
            nome='Nigiri', descricao='d', preco=Decimal('12.00'),
            categoria=self.categoria, imagem='',
        )

    def test_loja_fechada_marca_is_open_false(self):
        _horario_para_todos_os_dias(is_open=False)
        response = self.client.get(reverse('sushiemcasa:cardapio'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['is_open'])

    def test_loja_aberta_marca_is_open_true(self):
        _horario_para_todos_os_dias(
            is_open=True,
            open_time=datetime.time(0, 0),
            close_time=datetime.time(23, 59),
        )
        response = self.client.get(reverse('sushiemcasa:cardapio'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_open'])

    def test_cardapio_lista_apenas_produtos_disponiveis(self):
        Produto.objects.create(
            nome='Indisponível', descricao='d', preco=Decimal('9.00'),
            categoria=self.categoria, imagem='', disponivel=False,
        )
        response = self.client.get(reverse('sushiemcasa:cardapio'))
        nomes = [p.nome for p in response.context['produtos']]
        self.assertIn('Nigiri', nomes)
        self.assertNotIn('Indisponível', nomes)


# =========================================================================
# VIEW DE CHECKOUT
# =========================================================================
class CheckoutViewTests(TestCase):
    def test_carrinho_vazio_redireciona_para_basket(self):
        response = self.client.get(reverse('sushiemcasa:checkout'))
        self.assertRedirects(response, reverse('sushiemcasa:basket'))


# =========================================================================
# PAINEL DA LOJA (cadastros que substituem o Admin completo)
# =========================================================================
import io
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image

from sushiemcasa.models import BannerPromocional

MEDIA_TESTE = tempfile.mkdtemp()


def _imagem_png(nome='foto.png'):
    buf = io.BytesIO()
    Image.new('RGB', (10, 10), (200, 0, 0)).save(buf, format='PNG')
    return SimpleUploadedFile(nome, buf.getvalue(), content_type='image/png')


@override_settings(
    MEDIA_ROOT=MEDIA_TESTE,
    STORAGES={
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    },
)
class PainelGestaoTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_TESTE, ignore_errors=True)

    def setUp(self):
        self.admin = User.objects.create_superuser('chefe', 'chefe@example.com', 'senha-de-teste-123')
        self.staff = User.objects.create_user('equipe', 'equipe@example.com', 'senha-de-teste-123', is_staff=True)
        self.cliente = User.objects.create_user('cliente', 'cliente@example.com', 'senha-de-teste-123')
        self.categoria = Categoria.objects.create(nome='Temaki', slug='temaki')

    def test_paginas_do_painel_abrem_para_equipe(self):
        self.client.force_login(self.staff)
        for nome in ['listar_produtos', 'criar_produto', 'listar_categorias', 'criar_categoria',
                     'listar_banners', 'criar_banner', 'listar_mensagens', 'listar_usuarios']:
            with self.subTest(pagina=nome):
                self.assertEqual(self.client.get(reverse(f'sushiemcasa:{nome}')).status_code, 200)

    def test_cliente_nao_acessa_o_painel(self):
        self.client.force_login(self.cliente)
        response = self.client.get(reverse('sushiemcasa:listar_categorias'))
        self.assertRedirects(response, reverse('sushiemcasa:cardapio'))

    def test_criar_categoria_gera_link_pelo_nome(self):
        self.client.force_login(self.staff)
        self.client.post(reverse('sushiemcasa:criar_categoria'), {'nome': 'Hot Rolls', 'slug': ''})
        self.assertTrue(Categoria.objects.filter(nome='Hot Rolls', slug='hot-rolls').exists())

    def test_nao_apaga_categoria_com_produtos(self):
        Produto.objects.create(nome='Temaki', descricao='x', preco=Decimal('10'), categoria=self.categoria)
        self.client.force_login(self.staff)
        self.client.post(reverse('sushiemcasa:excluir_categoria', args=[self.categoria.pk]))
        self.assertTrue(Categoria.objects.filter(pk=self.categoria.pk).exists())
        self.assertEqual(Produto.objects.count(), 1)

    def test_criar_editar_e_apagar_produto(self):
        self.client.force_login(self.staff)
        self.client.post(reverse('sushiemcasa:criar_produto'), {
            'nome': 'Uramaki', 'categoria': self.categoria.pk, 'descricao': 'Novo',
            'preco': '12.50', 'imagem': _imagem_png(), 'disponivel': 'on',
        })
        produto = Produto.objects.get(nome='Uramaki')
        self.assertTrue(produto.imagem.name.startswith('produtos/'))

        self.client.post(reverse('sushiemcasa:editar_produto', args=[produto.pk]), {
            'nome': 'Uramaki', 'categoria': self.categoria.pk, 'descricao': 'Novo',
            'preco': '13.00',  # sem 'disponivel' = desmarcado; sem imagem = mantém a atual
        })
        produto.refresh_from_db()
        self.assertEqual(produto.preco, Decimal('13.00'))
        self.assertFalse(produto.disponivel)
        self.assertTrue(produto.imagem.name.startswith('produtos/'))

        self.client.post(reverse('sushiemcasa:excluir_produto', args=[produto.pk]))
        self.assertFalse(Produto.objects.filter(pk=produto.pk).exists())

    def test_excluir_so_por_post(self):
        produto = Produto.objects.create(nome='Hot', descricao='x', preco=Decimal('10'), categoria=self.categoria)
        self.client.force_login(self.staff)
        response = self.client.get(reverse('sushiemcasa:excluir_produto', args=[produto.pk]))
        self.assertEqual(response.status_code, 405)

    def test_criar_promocao(self):
        self.client.force_login(self.staff)
        self.client.post(reverse('sushiemcasa:criar_banner'), {
            'titulo': 'Combo', 'descricao': 'Oferta', 'imagem': _imagem_png('b.png'),
            'preco_promocional': '20', 'ordem': '1', 'ativo': 'on',
        })
        self.assertTrue(BannerPromocional.objects.filter(titulo='Combo', ativo=True).exists())

    def test_apagar_mensagem(self):
        msg = MensagemFeedback.objects.create(nome='Ana', mensagem='Oi')
        self.client.force_login(self.staff)
        self.client.post(reverse('sushiemcasa:excluir_mensagem', args=[msg.pk]))
        self.assertFalse(MensagemFeedback.objects.filter(pk=msg.pk).exists())

    def test_admin_da_e_tira_acesso_da_equipe(self):
        self.client.force_login(self.admin)
        url = reverse('sushiemcasa:alterar_usuario', args=[self.cliente.pk])
        self.client.post(url, {'campo': 'is_staff'})
        self.cliente.refresh_from_db()
        self.assertTrue(self.cliente.is_staff)
        self.client.post(url, {'campo': 'is_active'})
        self.cliente.refresh_from_db()
        self.assertFalse(self.cliente.is_active)

    def test_equipe_nao_altera_acessos(self):
        self.client.force_login(self.staff)
        self.client.post(reverse('sushiemcasa:alterar_usuario', args=[self.cliente.pk]), {'campo': 'is_staff'})
        self.cliente.refresh_from_db()
        self.assertFalse(self.cliente.is_staff)

    def test_admin_nao_altera_a_propria_conta(self):
        self.client.force_login(self.admin)
        self.client.post(reverse('sushiemcasa:alterar_usuario', args=[self.admin.pk]), {'campo': 'is_active'})
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)


# =========================================================================
# CORREÇÕES ACHADAS NO TESTE DO CAMINHO DO CLIENTE
# =========================================================================
class CheckoutSemDataTests(TestCase):
    def setUp(self):
        cat = Categoria.objects.create(nome='Uramaki', slug='uramaki')
        self.produto = Produto.objects.create(nome='Uramaki', descricao='x', preco=Decimal('10'), categoria=cat)
        self.client.post(reverse('sushiemcasa:add_to_cart', args=[self.produto.id]), {'quantity': 2})

    def test_sem_data_nao_quebra_nem_cria_pedido(self):
        response = self.client.post(reverse('sushiemcasa:checkout'), {'delivery_datetime': ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Choose a delivery date and time.')
        self.assertEqual(Order.objects.count(), 0)
        self.assertTrue(self.client.session.get('cart'))  # carrinho preservado


class DetalheDoPedidoAcessoTests(TestCase):
    def setUp(self):
        self.dono = User.objects.create_user('dono', password='senha-de-teste-123')
        self.outro = User.objects.create_user('outro', password='senha-de-teste-123')
        self.equipe = User.objects.create_user('equipe', password='senha-de-teste-123', is_staff=True)
        self.pedido = Order.objects.create(user=self.dono, total_price=Decimal('10'))
        self.url = reverse('sushiemcasa:order_detail', args=[self.pedido.id])

    def test_visitante_vai_para_o_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('sushiemcasa:login'), response['Location'])

    def test_outro_cliente_nao_ve(self):
        self.client.force_login(self.outro)
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_dono_ve(self):
        self.client.force_login(self.dono)
        self.assertEqual(self.client.get(self.url).status_code, 200)

    def test_equipe_ve(self):
        self.client.force_login(self.equipe)
        self.assertEqual(self.client.get(self.url).status_code, 200)


@override_settings(STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})
class TopoDoCardapioTests(TestCase):
    """O topo do cardápio quebrou em produção com banners cadastrados (QuerySet + |last)."""
    def setUp(self):
        cat = Categoria.objects.create(nome='Temaki', slug='temaki')
        Produto.objects.create(nome='Temaki', descricao='x', preco=Decimal('10'), categoria=cat, imagem='produtos/t.jpg')

    def test_sem_banners_usa_foto_do_produto(self):
        response = self.client.get(reverse('sushiemcasa:cardapio'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'produtos/t.jpg')

    def test_com_dois_banners_usa_o_segundo(self):
        BannerPromocional.objects.create(titulo='A', descricao='a', imagem='banners/a.jpg', preco_promocional=1, ordem=1)
        BannerPromocional.objects.create(titulo='B', descricao='b', imagem='banners/b.jpg', preco_promocional=1, ordem=2)
        response = self.client.get(reverse('sushiemcasa:cardapio'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['foto_topo'].name, 'banners/b.jpg')
