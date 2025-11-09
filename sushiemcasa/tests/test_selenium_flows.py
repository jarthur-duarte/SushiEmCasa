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
from sushiemcasa.models import Produto, Categoria, Order, HorarioDeFuncionamento # Adicionado Order

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
        
        HorarioDeFuncionamento.objects.all().delete()
        
        abertura = datetime.strptime('00:00', '%H:%M').time()
        fechamento = datetime.strptime('23:59', '%H:%M').time()

        for i in range(7): # 0=Segunda, 1=Terça, ..., 6=Domingo
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
    def test_finalizar_pedido_redireciona_para_whatsapp(self):
        
        self.client.post(reverse('sushiemcasa:add_to_cart', args=[self.produto1.id]), {'quantity': 1})
        
        checkout_url = self.live_server_url + reverse('sushiemcasa:checkout')
        self.driver.get(checkout_url)
        wait = WebDriverWait(self.driver, 10)
        
        now_aware = timezone.now()
        valid_datetime_aware = now_aware + timedelta(hours=25)
        valid_local_datetime = timezone.localtime(valid_datetime_aware)

        delivery_hour = valid_local_datetime.hour
        
        if not (10 <= delivery_hour < 20):
            valid_local_datetime += timedelta(days=1)
            valid_local_datetime = valid_local_datetime.replace(hour=14, minute=0, second=0, microsecond=0)
        
        while valid_local_datetime.weekday() == 6:
            valid_local_datetime += timedelta(days=1)
            
        datetime_string = valid_local_datetime.strftime('%Y-%m-%dT%H:%M')
        
        campo_data = wait.until(EC.presence_of_element_located((By.ID, 'id_delivery_datetime')))
        
        self.driver.execute_script("arguments[0].value = arguments[1]", campo_data, datetime_string)
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('input'))", campo_data)

        try:
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn-submit')))
        except TimeoutException:
            self.fail("O Selenium preencheu a data, mas o JavaScript não habilitou o botão 'Confirmar'.")

        btn_confirmar = self.driver.find_element(By.CSS_SELECTOR, '.btn-submit')
        btn_confirmar.click()

        wait_externo = WebDriverWait(self.driver, 20) 
        
        try:
            wait_externo.until(EC.url_contains('whatsapp.com'))
            
            url_atual = self.driver.current_url
            
            self.assertIn('5587988240512', url_atual)
            self.assertIn('Novo+Pedido+Agendado', url_atual)
            self.assertIn('Teste+Sushi', url_atual) 
            self.assertIn('10.00', url_atual) 

        except TimeoutException:
            error_text = "Nenhuma mensagem de erro de formulário foi encontrada."
            try:
                error_elements = self.driver.find_elements(By.CSS_SELECTOR, '.errorlist p')
                message_elements = self.driver.find_elements(By.CSS_SELECTOR, 'ul.messages li')
                
                all_errors = error_elements + message_elements
                if all_errors:
                    error_text = "\n".join([e.text for e in all_errors])

            except Exception as e:
                error_text = f"Erro ao tentar encontrar a mensagem de erro: {e}"

            self.fail(
                "O Selenium clicou em 'Confirmar', mas não foi redirecionado.\n"
                f"URL ATUAL: {self.driver.current_url}\n"
                f"ERRO DE VALIDAÇÃO ENCONTRADO NA PÁGINA: '{error_text}'"
            )
            
        ultimo_pedido = Order.objects.filter(user=self.user).order_by('-id').first()
        self.assertIsNotNone(ultimo_pedido, "O pedido não foi salvo no banco de dados.")
        self.assertEqual(ultimo_pedido.total_price, Decimal('10.00'))
class HorarioFuncionamentoSeleniumTests(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        """
        Inicia o driver UMA VEZ para todos os testes desta classe.
        """
        super().setUpClass()
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless') 
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        service = ChromeService(ChromeDriverManager().install())
        cls.driver = webdriver.Chrome(service=service, options=options)
        cls.driver.implicitly_wait(10) # Usar uma espera um pouco maior é bom

    @classmethod
    def tearDownClass(cls):
        """
        Fecha o driver UMA VEZ após todos os testes rodarem.
        """
        cls.driver.quit()
        super().tearDownClass()

    # REMOVA o método tearDown(self)
    # def tearDown(self): ...

    # --- Funções Auxiliares ---
    
    def _login_admin(self):
        """Uma função helper para logar como admin."""
        # MUDANÇA: de 'self.browser' para 'self.driver'
        self.driver.get(self.live_server_url + '/admin/login/')
        
        self.driver.find_element(By.ID, 'id_username').send_keys(self.admin_user.username)
        self.driver.find_element(By.ID, 'id_password').send_keys('adminpassword')
        self.driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()
        
        WebDriverWait(self.driver, 10).until( # Aumentei para 10s
            EC.presence_of_element_located((By.ID, 'user-tools'))
        )
        
    def test_cenario_5_horario_fechamento_anterior_abertura(self):
        # Dado que a administradora está logada
        self._login_admin()

        # --- CORREÇÃO: Encontrar o objeto "Quinta-feira" (day_of_week=3) ---
        try:
            quinta = HorarioDeFuncionamento.objects.get(day_of_week=3)
        except HorarioDeFuncionamento.DoesNotExist:
            self.fail("O setUp não criou o registro para Quinta-feira (day_of_week=3).")

        # Quando ela acessa a página de EDIÇÃO deste objeto
        url_admin_horario = f'{self.live_server_url}/admin/sushiemcasa/horariodefuncionamento/{quinta.pk}/change/'
        self.driver.get(url_admin_horario)

        # E ela insere o horário de abertura como "18:00" e o de fechamento como "16:00"
        # Os nomes dos campos no admin do Django são padronizados
        
        campo_abertura = self.driver.find_element(By.ID, 'id_open_time')
        campo_fechamento = self.driver.find_element(By.ID, 'id_close_time')
        # Precisamos marcar a caixa "Aberto?"
        campo_status = self.driver.find_element(By.ID, 'id_is_open')

        if not campo_status.is_selected():
             campo_status.click() # Marca a caixa "Aberto?"

        campo_abertura.clear()
        campo_abertura.send_keys('18:00:00')
        campo_fechamento.clear()
        campo_fechamento.send_keys('16:00:00')

        # E clica em salvar
        self.driver.find_element(By.NAME, '_save').click()
        
        # Então o sistema deve exibir uma mensagem de erro
        # (A lógica de verificação de erro permanece a mesma)
        
        # NOTA: A sua validação está no método clean(). Erros de clean()
        # podem aparecer em 'errornote' (geral) ou perto do campo.
        # Vamos procurar em ambos.
        
        try:
            WebDriverWait(self.driver, 5).until(
                # Procura ou um 'errornote' geral ou um erro de campo
                EC.presence_of_element_located((
                    By.CSS_SELECTOR, '.errornote, .errorlist'
                ))
            )
            
            error_elements = self.driver.find_elements(By.CSS_SELECTOR, '.errornote, .errorlist')
            
            # Junta o texto de todos eles
            all_error_text = " ".join([e.text for e in error_elements])
            
            # Verifica se a sua mensagem específica está no texto combinado
            self.assertIn('O horário de fechamento não pode ser anterior ou igual ao de abertura', all_error_text)

        except TimeoutException:
            self.fail("A página não exibiu uma mensagem de erro (errornote ou errorlist) após 5 segundos.")
        
    def _login_cliente(self):
        """
        Faz login do cliente (self.client_user) via cookie injection.
        É muito mais rápido que preencher o formulário de login.
        """
        # 1. Usa o 'self.client' do Django para fazer o login no backend
        #    Usamos o 'username' que definimos no setUp
        login_success = self.client.login(
            username=self.client_user.username, 
            password='clientpassword'
        )
        
        # Garante que o login funcionou
        self.assertTrue(login_success, "Login do cliente no backend falhou.")
        
        # 2. Pega o cookie da sessão
        cookie = self.client.cookies.get('sessionid')
        
        if not cookie:
            self.fail("Não foi possível fazer login e pegar o sessionid cookie.")

        # 3. Injeta o cookie no driver do Selenium
        #    Primeiro, precisamos visitar uma página do domínio
        #    Vou usar 'cardapio' como no seu outro teste
        try:
            cardapio_url = self.live_server_url + reverse('sushiemcasa:cardapio')
        except Exception as e:
            self.fail(f"Não foi possível reverter a URL 'sushiemcasa:cardapio'. Verifique seu urls.py. Erro: {e}")
            
        self.driver.get(cardapio_url) 
        
        self.driver.add_cookie({
            'name': 'sessionid',
            'value': cookie.value,
            'path': '/',
            # Ajuste de domínio como no seu outro teste
            'domain': self.live_server_url.split(':')[1].replace("//","") 
        })
        
        # 4. Recarrega a página, agora logado
        self.driver.get(cardapio_url)
        
        # Pequena espera para garantir que a página logada carregou
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
    
    def setUp(self):
        """
        Configuração inicial de DADOS que roda antes de CADA teste.
        O driver (self.driver) já existe e será reutilizado.
        """
        super().setUp() # Importante

        # --- Crie os dados necessários para os testes ---

        # 1. Crie um Superusuário (Admin)
        self.admin_user = User.objects.create_superuser(
            email='admin@sushi.com',
            password='adminpassword',
            username='adminuser'
        )

        # 2. Crie um Cliente
        self.client_user = User.objects.create_user(
            email='cliente@email.com',
            password='clientpassword',
            username='clientuser'
        )
        
        HorarioDeFuncionamento.objects.all().delete()

        # 3. Crie a configuração de horário PADRÃO (FECHADO)
        for i in range(7): # 0=Segunda, 1=Terça, ..., 6=Domingo
            HorarioDeFuncionamento.objects.create(
                day_of_week=i,
                is_open=False,
                open_time=None,  # Como no seu método clean()
                close_time=None
        )

        # --- 4. ADICIONE DADOS PARA O TESTE DE CHECKOUT ---
        # (Necessário para o Cenário 2)
        
        self.categoria = Categoria.objects.create(nome='Test Categoria', slug='test-categoria')
        
        self.produto1 = Produto.objects.create(
            nome='Produto Teste Loja Fechada',
            preco=Decimal('25.00'),
            categoria=self.categoria,
            descricao='Desc teste.',
            imagem='' # Adicione se for obrigatório
        )
    
    # (Dentro da classe HorarioFuncionamentoSeleniumTests)

    def test_cenario_2_e_3_cliente_ve_loja_fechada_e_pedido_bloqueado(self):
        # Dado que a loja está fechada (feito no self.setUp)
        # E que o cliente está logado
        self._login_cliente() # Usa a nova função helper
        
        # O helper de login já nos leva para a página do cardápio

        # === Verificação do Cenário 3 (Aviso na Página) ===
        
        # O seletor correto agora é para a mensagem do Django
        aviso_seletor = (By.CSS_SELECTOR, 'li.message') 
        
        try:
            aviso = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(aviso_seletor)
            )
            # Verifica se a view 'cardapio' enviou a mensagem correta
            self.assertIn('loja fechada', aviso.text.lower())
            
        except TimeoutException:
            self.fail(f"NÃO FOI POSSÍVEL ENCONTRAR O AVISO DE 'LOJA FECHADA' (seletor: li.message).\n"
                      f"Verifique se sua view 'cardapio' está enviando uma 'messages.warning' quando a loja está fechada.")

        # === Verificação do Cenário 2 (Bloqueio no Checkout) ===
        
        # 1. Adicionar o item ao carrinho
        self.client.post(reverse('sushiemcasa:add_to_cart', args=[self.produto1.id]), {'quantity': 1})

        # 2. Quando um cliente tenta realizar um pedido (vai para o checkout)
        checkout_url = self.live_server_url + reverse('sushiemcasa:checkout')
        self.driver.get(checkout_url)

        # 3. Então o sistema deve impedir a finalização
        # (O seletor .btn-submit está correto)
        botao_seletor = (By.CSS_SELECTOR, '.btn-submit') 

        try:
            botao_finalizar = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(botao_seletor)
            )
            
            # Checa se o botão tem o atributo 'disabled'
            is_disabled = botao_finalizar.get_attribute('disabled')
            
            self.assertTrue(
                is_disabled, 
                "O botão 'Finalizar Pedido' deveria estar desabilitado (ter o atributo 'disabled'), mas não está."
            )
            
        except TimeoutException:
            self.fail(f"NÃO FOI POSSÍVEL ENCONTRAR O BOTÃO 'FINALIZAR PEDIDO'.\n"
                      f"Verifique o seletor: {botao_seletor}")

    def test_cliente_pode_finalizar_pedido_com_loja_aberta(self):
        # 1. Dado: A loja está ABERTA
        # O setUp() cria a loja como 'fechado', então
        # precisamos ativamente ABRIR a loja para este teste.
        
        abertura = datetime.strptime('09:00', '%H:%M').time()
        fechamento = datetime.strptime('23:00', '%H:%M').time()
        
        try:
            # Pega todos os 7 registros criados no setUp
            horarios = HorarioDeFuncionamento.objects.all()
            for horario_dia in horarios:
                horario_dia.is_open = True
                horario_dia.open_time = abertura
                horario_dia.close_time = fechamento
                horario_dia.save() # Salva cada objeto
        
        except Exception as e:
            self.fail(f"Falha ao atualizar horários para 'aberto' no banco de dados. Erro: {e}")

        # O resto do teste (do ponto 2 em diante) permanece
        # EXATAMENTE IGUAL, pois ele testa a interface do cliente,
        # que não mudou.

        # 2. Quando: O cliente faz login
        self._login_cliente()

        # 3. Então: Ele NÃO deve ver o aviso de loja fechada
        aviso_seletor = (By.CSS_SELECTOR, 'li.message')
        
        try:
            WebDriverWait(self.driver, 5).until(
                EC.invisibility_of_element_located(aviso_seletor)
            )
        except TimeoutException:
            self.fail(f"O AVISO DE 'LOJA FECHADA' FOI ENCONTRADO, mas a loja deveria estar aberta.")

        # 4. E Quando: Ele adiciona um item e vai para o checkout
        self.client.post(reverse('sushiemcasa:add_to_cart', args=[self.produto1.id]), {'quantity': 1})
        checkout_url = self.live_server_url + reverse('sushiemcasa:checkout')
        self.driver.get(checkout_url)

        # 5. Então: O botão de finalizar pedido deve estar ATIVADO
        botao_seletor = (By.CSS_SELECTOR, '.btn-submit')
        try:
            botao_finalizar = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(botao_seletor)
            )
            is_disabled = botao_finalizar.get_attribute('disabled')
            self.assertFalse(
                is_disabled, 
                "O botão 'Finalizar Pedido' deveria estar HABILITADO, mas está desabilitado."
            )
        except TimeoutException:
            self.fail(f"Não foi possível encontrar o botão 'Finalizar Pedido'. Seletor: {botao_seletor}")

        # 6. E: Ele pode finalizar o pedido com sucesso
        
        # --- Gera uma data de entrega válida ---
        now_aware = timezone.now()
        
        # 1. Garante que está 25h no futuro
        valid_datetime_aware = now_aware + timedelta(hours=25)
        valid_local_datetime = timezone.localtime(valid_datetime_aware)

        # 2. Garante que está dentro da janela de entrega (ex: 10:00 - 20:00)
        #    (Usei a janela 10-20 do seu outro teste, ajuste se necessário)
        delivery_hour = valid_local_datetime.hour
        if not (10 <= delivery_hour < 20):
            # Se a hora caiu fora, ajusta para o próximo dia às 14:00
            valid_local_datetime += timedelta(days=1)
            while valid_local_datetime.weekday() == 6: # 6 é Domingo
                valid_local_datetime += timedelta(days=1)
            
            valid_local_datetime = valid_local_datetime.replace(hour=14, minute=0, second=0, microsecond=0)

        datetime_string = valid_local_datetime.strftime('%Y-%m-%dT%H:%M')
        # --- Fim da geração de data ---

        # Preenche o formulário
        campo_data = self.driver.find_element(By.ID, 'id_delivery_datetime')
        self.driver.execute_script("arguments[0].value = arguments[1]", campo_data, datetime_string)

        self.driver.find_element(By.CSS_SELECTOR, '.btn-submit').click()

        # Verifica o sucesso
        try:
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.url_contains('/order/'))
            
            mensagem_sucesso_element = wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'ul.messages li.success'))
            )
            self.assertIn('realizado com sucesso', mensagem_sucesso_element.text.lower())
        
        except TimeoutException:
            form_errors = self.driver.find_elements(By.CSS_SELECTOR, '.errorlist')
            error_text = "\n".join([err.text for err in form_errors])
            self.fail(f"O pedido não foi finalizado com sucesso (LOJA ABERTA).\n"
                      f"URL atual: {self.driver.current_url}\n"
                      f"Erros encontrados no formulário:\n{error_text}\n")


