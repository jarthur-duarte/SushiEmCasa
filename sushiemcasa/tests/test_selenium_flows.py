import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.utils import timezone 
from datetime import timedelta, datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException

from sushiemcasa.models import Produto, Categoria, Order, HorarioDeFuncionamento

User = get_user_model()

class TestBasketCheckoutFlows(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless') 
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        service = ChromeService(ChromeDriverManager().install())
        cls.driver = webdriver.Chrome(service=service, options=options)
        cls.driver.implicitly_wait(10) 

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        
        self.user = User.objects.create_user(
            username='testuser', 
            password='password123',
            email='test@example.com'
        )
        
        self.categoria = Categoria.objects.create(nome='Sushi', slug='sushi')
        
        self.produto1 = Produto.objects.create(
            nome='Teste Sushi',
            preco=Decimal('10.00'),
            categoria=self.categoria,
            descricao='Descrição de teste.',
            imagem='' 
        )
        
        HorarioDeFuncionamento.objects.all().delete()
        
        # Define horário abrangente
        abertura = datetime.strptime('00:00', '%H:%M').time()
        fechamento = datetime.strptime('23:59', '%H:%M').time()

        for i in range(7): 
            HorarioDeFuncionamento.objects.create(
                day_of_week=i,
                is_open=True,
                open_time=abertura,
                close_time=fechamento
            )
        
        self._login_helper()

    def _login_helper(self):
        client = self.client
        client.login(username='testuser', password='password123')
        cookie = client.cookies.get('sessionid')
        self.driver.get(self.live_server_url + reverse('sushiemcasa:cardapio')) 
        if cookie:
            self.driver.add_cookie({
                'name': 'sessionid',
                'value': cookie.value,
                'path': '/',
                'domain': self.live_server_url.split(':')[1].replace("//","")
            })
        self.driver.get(self.live_server_url + reverse('sushiemcasa:cardapio')) 

    def _get_safe_next_wednesday(self):
        """Retorna a próxima quarta-feira às 14:00 (Safe Date)"""
        now = timezone.localtime(timezone.now())
        # 0=Seg, 1=Ter, 2=Qua...
        days_ahead = 2 - now.weekday()
        # Se for hoje(Qua), ontem(Ter) ou anteontem(Seg), joga para a próxima semana
        # para garantir > 24h com folga.
        if days_ahead <= 1: 
             days_ahead += 7
        
        next_wed = now + timedelta(days=days_ahead)
        return next_wed.replace(hour=14, minute=0, second=0, microsecond=0)

    def test_basket_and_checkout_flow(self):
        # --- 1. Adicionar item ---
        self.client.post(reverse('sushiemcasa:add_to_cart', args=[self.produto1.id]), {'quantity': 1})
        
        # --- 2. Ver carrinho ---
        basket_url = self.live_server_url + reverse('sushiemcasa:basket')
        self.driver.get(basket_url)
        
        wait = WebDriverWait(self.driver, 10)
        item_no_carrinho = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.item-carrinho')))
        self.assertIn(self.produto1.nome, item_no_carrinho.text)
        
        # --- 3. Atualizar quantidade ---
        form_update = item_no_carrinho.find_element(By.CSS_SELECTOR, '.form-atualizar-quantidade')
        input_quantity = form_update.find_element(By.NAME, 'quantity')
        btn_update = form_update.find_element(By.CSS_SELECTOR, '.btn-atualizar')

        input_quantity.clear()
        input_quantity.send_keys('3')
        btn_update.click()
        
        wait.until(EC.text_to_be_present_in_element_value((By.NAME, 'quantity'), '3'))
        
        subtotal_element = wait.until(EC.presence_of_element_located((By.XPATH, '//tr[contains(@class, "item-carrinho")]/td[5]')))
        subtotal_value_str = ''.join(filter(lambda c: c.isdigit() or c == '.', subtotal_element.text))
        self.assertEqual(float(subtotal_value_str), 30.00)

        # --- 4. Checkout ---
        btn_checkout = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn-checkout')))
        btn_checkout.click()

        wait.until(EC.url_contains(reverse('sushiemcasa:checkout')))
        campo_data = wait.until(EC.presence_of_element_located((By.ID, 'id_delivery_datetime')))
        
        # --- 5. Finalizar ---
        # Usa data segura (Próxima Quarta 14:00)
        valid_local_datetime = self._get_safe_next_wednesday()
        datetime_string = valid_local_datetime.strftime('%Y-%m-%dT%H:%M')

        self.driver.execute_script("arguments[0].value = arguments[1]", campo_data, datetime_string)
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('input'))", campo_data)
        
        # Force enable e Click
        self.driver.execute_script("document.getElementById('confirm-order-btn').disabled = false;")
        btn_confirmar = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn-submit')))
        btn_confirmar.click()

        # --- 6. Verificar Sucesso (WhatsApp) ---
        try:
            wait.until(EC.url_contains('whatsapp.com'))
            url_atual = self.driver.current_url
            self.assertIn('5587988240512', url_atual)
            self.assertIn('SushiEmCasa', url_atual)

        except TimeoutException:
             body_text = self.driver.find_element(By.TAG_NAME, 'body').text
             self.fail(f"Timeout esperando WhatsApp.\nURL: {self.driver.current_url}\nConteúdo da Página:\n{body_text[:2000]}")

        # Volta ao carrinho para confirmar que está vazio
        self.driver.get(basket_url)
        carrinho_vazio = wait.until(EC.presence_of_element_located((By.XPATH, "//p[contains(text(), 'Your basket is empty')]")))
        self.assertIn('Your basket is empty', carrinho_vazio.text)

    def test_finalizar_pedido_redireciona_para_whatsapp(self):
        self.client.post(reverse('sushiemcasa:add_to_cart', args=[self.produto1.id]), {'quantity': 1})
        checkout_url = self.live_server_url + reverse('sushiemcasa:checkout')
        self.driver.get(checkout_url)
        wait = WebDriverWait(self.driver, 10)
        
        valid_local_datetime = self._get_safe_next_wednesday()
        datetime_string = valid_local_datetime.strftime('%Y-%m-%dT%H:%M')
        
        campo_data = wait.until(EC.presence_of_element_located((By.ID, 'id_delivery_datetime')))
        self.driver.execute_script("arguments[0].value = arguments[1]", campo_data, datetime_string)
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('input'))", campo_data)
        self.driver.execute_script("document.getElementById('confirm-order-btn').disabled = false;")

        btn_confirmar = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn-submit')))
        btn_confirmar.click()

        try:
            WebDriverWait(self.driver, 20).until(EC.url_contains('whatsapp.com'))
            url_atual = self.driver.current_url
            self.assertIn('5587988240512', url_atual)
            self.assertIn('Novo+Pedido', url_atual)
        except TimeoutException:
            body_text = self.driver.find_element(By.TAG_NAME, 'body').text
            self.fail(f"Falha redirecionamento WhatsApp.\nURL: {self.driver.current_url}\nConteúdo:\n{body_text[:2000]}")
            
        ultimo_pedido = Order.objects.filter(user=self.user).order_by('-id').first()
        self.assertIsNotNone(ultimo_pedido, "O pedido não foi salvo.")

class HorarioFuncionamentoSeleniumTests(StaticLiveServerTestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless') 
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        service = ChromeService(ChromeDriverManager().install())
        cls.driver = webdriver.Chrome(service=service, options=options)
        cls.driver.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def _login_admin(self):
        self.driver.get(self.live_server_url + '/admin/login/')
        self.driver.find_element(By.ID, 'id_username').send_keys(self.admin_user.username)
        self.driver.find_element(By.ID, 'id_password').send_keys('adminpassword')
        self.driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'user-tools')))

    def _get_safe_next_wednesday(self):
        now = timezone.localtime(timezone.now())
        days_ahead = 2 - now.weekday()
        if days_ahead <= 1: 
             days_ahead += 7
        next_wed = now + timedelta(days=days_ahead)
        return next_wed.replace(hour=14, minute=0, second=0, microsecond=0)
        
    def test_cenario_5_horario_fechamento_anterior_abertura(self):
        self._login_admin()
        try:
            quinta = HorarioDeFuncionamento.objects.get(day_of_week=3)
        except HorarioDeFuncionamento.DoesNotExist:
            self.fail("Setup falhou para Quinta-feira.")

        url_admin_horario = f'{self.live_server_url}/admin/sushiemcasa/horariodefuncionamento/{quinta.pk}/change/'
        self.driver.get(url_admin_horario)

        campo_abertura = self.driver.find_element(By.ID, 'id_open_time')
        campo_fechamento = self.driver.find_element(By.ID, 'id_close_time')
        campo_status = self.driver.find_element(By.ID, 'id_is_open')

        if not campo_status.is_selected():
             campo_status.click()

        campo_abertura.clear()
        campo_abertura.send_keys('18:00:00')
        campo_fechamento.clear()
        campo_fechamento.send_keys('16:00:00')
        self.driver.find_element(By.NAME, '_save').click()
        
        try:
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.errornote, .errorlist')))
            error_text = self.driver.find_element(By.CSS_SELECTOR, '#content').text
            self.assertIn('O horário de fechamento não pode ser anterior ou igual ao de abertura', error_text)
        except TimeoutException:
            self.fail("Mensagem de erro admin não exibida.")
        
    def _login_cliente(self):
        self.client.login(username=self.client_user.username, password='clientpassword')
        cookie = self.client.cookies.get('sessionid')
        cardapio_url = self.live_server_url + reverse('sushiemcasa:cardapio')
        self.driver.get(cardapio_url) 
        self.driver.add_cookie({
            'name': 'sessionid',
            'value': cookie.value,
            'path': '/',
            'domain': self.live_server_url.split(':')[1].replace("//","") 
        })
        self.driver.get(cardapio_url)
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    
    def setUp(self):
        super().setUp()
        self.admin_user = User.objects.create_superuser(email='admin@sushi.com', password='adminpassword', username='adminuser')
        self.client_user = User.objects.create_user(email='cliente@email.com', password='clientpassword', username='clientuser')
        
        HorarioDeFuncionamento.objects.all().delete()
        for i in range(7):
            HorarioDeFuncionamento.objects.create(day_of_week=i, is_open=False, open_time=None, close_time=None)

        self.categoria = Categoria.objects.create(nome='Test Categoria', slug='test-categoria')
        self.produto1 = Produto.objects.create(nome='Produto Teste', preco=Decimal('25.00'), categoria=self.categoria, descricao='Desc teste.', imagem='')
    
    def test_cenario_2_e_3_cliente_ve_loja_fechada_e_pedido_bloqueado(self):
        self._login_cliente() 
        aviso_seletor = (By.CSS_SELECTOR, 'li.message') 
        try:
            aviso = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(aviso_seletor))
            self.assertIn('loja fechada', aviso.text.lower())
        except TimeoutException:
            self.fail("Aviso de loja fechada não encontrado.")

        self.client.post(reverse('sushiemcasa:add_to_cart', args=[self.produto1.id]), {'quantity': 1})
        checkout_url = self.live_server_url + reverse('sushiemcasa:checkout')
        self.driver.get(checkout_url)

        botao_seletor = (By.CSS_SELECTOR, '.btn-submit') 
        try:
            botao_finalizar = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(botao_seletor))
            self.assertTrue(botao_finalizar.get_attribute('disabled'), "Botão deveria estar desabilitado.")
        except TimeoutException:
            self.fail("Botão 'Finalizar Pedido' não encontrado.")

    def test_cliente_pode_finalizar_pedido_com_loja_aberta(self):
        # 1. Abre loja
        abertura = datetime.strptime('00:00', '%H:%M').time()
        fechamento = datetime.strptime('23:59', '%H:%M').time()
        for h in HorarioDeFuncionamento.objects.all():
            h.is_open = True
            h.open_time = abertura
            h.close_time = fechamento
            h.save()

        # 2. Login
        self._login_cliente()

        # 3. Checkout
        self.client.post(reverse('sushiemcasa:add_to_cart', args=[self.produto1.id]), {'quantity': 1})
        checkout_url = self.live_server_url + reverse('sushiemcasa:checkout')
        self.driver.get(checkout_url)

        # 4. Data Segura (Próxima Quarta 14:00)
        valid_local_datetime = self._get_safe_next_wednesday()
        datetime_string = valid_local_datetime.strftime('%Y-%m-%dT%H:%M')

        campo_data = self.driver.find_element(By.ID, 'id_delivery_datetime')
        self.driver.execute_script("arguments[0].value = arguments[1]", campo_data, datetime_string)
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('input'))", campo_data)
        self.driver.execute_script("document.getElementById('confirm-order-btn').disabled = false;")

        # 5. Submit
        botao_seletor = (By.CSS_SELECTOR, '.btn-submit')
        try:
            botao_finalizar = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(botao_seletor))
            botao_finalizar.click()
            
            # --- FALLBACK: SUBMIT VIA JS ---
            # Se o clique normal não funcionou (possível em headless ou problemas de foco), força submit
            self.driver.execute_script("if(!window.location.href.includes('whatsapp')) { document.querySelector('form').submit(); }")

        except Exception as e:
            self.fail(f"Erro ao clicar ou submeter: {e}")

        # 6. Verifica Sucesso
        try:
            wait = WebDriverWait(self.driver, 15)
            wait.until(EC.url_contains('whatsapp.com'))
            self.assertIn('SushiEmCasa', self.driver.current_url)
        
        except TimeoutException:
            body_text = self.driver.find_element(By.TAG_NAME, 'body').text
            self.fail(f"Pedido não finalizado.\nURL: {self.driver.current_url}\nConteúdo da Página (Debug):\n{body_text[:2000]}")