import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
# Imports adicionados/modificados
from django.utils import timezone 
from datetime import timedelta, datetime # Adicionado datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException

# Importe seus modelos
from sushiemcasa.models import Produto, Categoria, Order # Adicionado Order

User = get_user_model()

class TestBasketCheckoutFlows(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = webdriver.ChromeOptions()
        # Remova ou comente a linha '--headless' para ver o navegador durante o teste
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
        self._login_helper()

    def _login_helper(self):
        client = self.client
        client.login(username='testuser', password='password123')
        cookie = client.cookies.get('sessionid')
        self.driver.get(self.live_server_url + reverse('sushiemcasa:cardapio')) # Precisa carregar uma página do domínio primeiro
        if cookie:
            self.driver.add_cookie({
                'name': 'sessionid',
                'value': cookie.value,
                'path': '/',
                'domain': self.live_server_url.split(':')[1].replace("//","") # Adicione o domínio
            })
        self.driver.get(self.live_server_url + reverse('sushiemcasa:cardapio')) # Recarregue a página com o cookie

    def test_basket_and_checkout_flow(self):
        """
        Testa o fluxo completo:
        1. Adicionar item (via POST direto para simplicidade)
        2. Ver carrinho (basket.html)
        3. Atualizar quantidade
        4. Ir para checkout (checkout.html)
        5. Finalizar pedido
        6. Verificar sucesso e carrinho vazio
        """
        
        # --- 1. Adicionar item ao carrinho ---
        self.client.post(reverse('sushiemcasa:add_to_cart', args=[self.produto1.id]), {'quantity': 1})
        
        # --- 2. Ver carrinho (basket.html) ---
        basket_url = self.live_server_url + reverse('sushiemcasa:basket')
        self.driver.get(basket_url)
        
        wait = WebDriverWait(self.driver, 10)
        item_no_carrinho = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.item-carrinho'))
        )
        self.assertIn(self.produto1.nome, item_no_carrinho.text)
        
        # --- 3. Atualizar quantidade (basket.html) ---
        form_update = item_no_carrinho.find_element(By.CSS_SELECTOR, '.form-atualizar-quantidade')
        input_quantity = form_update.find_element(By.NAME, 'quantity')
        btn_update = form_update.find_element(By.CSS_SELECTOR, '.btn-atualizar')

        input_quantity.clear()
        input_quantity.send_keys('3')
        btn_update.click()

        wait.until(EC.staleness_of(item_no_carrinho)) 
        
        input_quantity_updated = wait.until(
            EC.presence_of_element_located((By.NAME, 'quantity'))
        )
        self.assertEqual(input_quantity_updated.get_attribute('value'), '3')
        
        subtotal_updated_text = wait.until(
            EC.presence_of_element_located((By.XPATH, '//tr[contains(@class, "item-carrinho")]/td[5]'))
        ).text
        # Extrair apenas o número do texto (ex: "R$ 30.00")
        subtotal_value_str = ''.join(filter(lambda c: c.isdigit() or c == '.', subtotal_updated_text))
        self.assertEqual(float(subtotal_value_str), 30.00)

        # --- 4. Ir para checkout (checkout.html) ---
        btn_checkout = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn-checkout')))
        btn_checkout.click()

        # Espera a página de checkout carregar
        wait.until(EC.url_contains(reverse('sushiemcasa:checkout')))
        # Verificar o título ou um elemento específico da página de checkout
        wait.until(EC.presence_of_element_located((By.ID, 'id_delivery_datetime'))) 
        
        # --- 5. Finalizar pedido (checkout.html) ---
        resumo_pedido = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.items-list'))
        ).text
        self.assertIn('3x Teste Sushi', resumo_pedido)
        total_text = self.driver.find_element(By.CSS_SELECTOR, '.pedido p strong').text
        total_value_str = ''.join(filter(lambda c: c.isdigit() or c == '.', total_text))
        self.assertEqual(float(total_value_str), 30.00) # Atenção: use float() para comparar números decimais

        # GERA UMA DATA VÁLIDA:
        # Pega a hora atual (ciente do fuso)
        now_aware = timezone.now()

        # 1. Garante que está 25h no futuro (para passar na regra de 24h)
        valid_datetime_aware = now_aware + timedelta(hours=25)

        # Converte para o fuso horário local
        valid_local_datetime = timezone.localtime(valid_datetime_aware)

        # 2. Garante que está dentro da janela de 10:00 - 20:00
        delivery_hour = valid_local_datetime.hour
        if not (10 <= delivery_hour < 20):
            # Se a hora caiu fora (ex: 9:00 ou 21:00), ajusta para o próximo dia útil às 14:00
            # Adiciona um dia até encontrar um dia que não seja domingo (weekday 6)
            valid_local_datetime += timedelta(days=1)
            while valid_local_datetime.weekday() == 6: # 6 é Domingo
                valid_local_datetime += timedelta(days=1)
            # Define um horário seguro dentro da janela (ex: 14:00)
            valid_local_datetime = valid_local_datetime.replace(hour=14, minute=0, second=0, microsecond=0)

        # Formata para o padrão YYYY-MM-DDTHH:MM
        datetime_string = valid_local_datetime.strftime('%Y-%m-%dT%H:%M')

        """ # Debug prints (remova ou comente após verificar)
        print(f"Current local time: {timezone.localtime(now_aware).strftime('%Y-%m-%dT%H:%M:%S %Z%z')}")
        print(f"Calculated valid local datetime: {valid_local_datetime.strftime('%Y-%m-%dT%H:%M')}")
        print(f"Datetime string being sent: {datetime_string}") """

        # Preenche o formulário via JavaScript
        campo_data = self.driver.find_element(By.ID, 'id_delivery_datetime')
        self.driver.execute_script("arguments[0].value = arguments[1]", campo_data, datetime_string)

        # Pequena pausa opcional
        # time.sleep(0.5)

        # Clica em confirmar pedido
        btn_confirmar = self.driver.find_element(By.CSS_SELECTOR, '.btn-submit')
        btn_confirmar.click()

        # --- 6. Verificar sucesso e carrinho vazio ---
        try:
            # Espera o redirecionamento para a página de detalhes do pedido
            wait.until(EC.url_contains('/order/'))

            # Verifica a mensagem de sucesso
            mensagem_sucesso_element = wait.until(
                 # Usa um seletor CSS mais específico para a mensagem de sucesso
                 EC.visibility_of_element_located((By.CSS_SELECTOR, 'ul.messages li.success'))
            )
            mensagem_sucesso = mensagem_sucesso_element.text
            self.assertIn('realizado com sucesso', mensagem_sucesso.lower())

        except TimeoutException:
             # Se a página de sucesso não carregar ou a mensagem não aparecer, falha o teste
             page_source = self.driver.page_source # Pega o HTML da página atual
             # Tenta encontrar mensagens de erro do formulário no código-fonte
             form_errors = self.driver.find_elements(By.CSS_SELECTOR, '.errorlist')
             error_text = "\n".join([err.text for err in form_errors])
             self.fail(f"Timeout esperando pela página de confirmação do pedido ou pela mensagem de sucesso.\n"
                       f"URL atual: {self.driver.current_url}\n"
                       f"Erros encontrados no formulário:\n{error_text}\n"
                       f"Page Source Snippet:\n{page_source[:1000]}...") # Mostra o início do HTML para diagnóstico

        # Agora, visita o carrinho novamente para garantir que está vazio
        self.driver.get(basket_url)
        carrinho_vazio_msg_element = wait.until(
            EC.presence_of_element_located((By.XPATH, "//p[contains(text(), 'Your basket is empty')]"))
        )
        carrinho_vazio_msg = carrinho_vazio_msg_element.text
        self.assertIn('Your basket is empty', carrinho_vazio_msg)
