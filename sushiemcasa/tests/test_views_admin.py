from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

# Importe os modelos que você vai usar
from sushiemcasa.models.produtos import Produto, Categoria

User = get_user_model()


class TestGerenciamentoProdutos(TestCase):

    def setUp(self):
        # ... (seu self.client, self.admin_user, self.regular_user ...
        # estão corretos)
        self.client = Client()
        self.admin_user = User.objects.create_superuser(...)
        self.regular_user = User.objects.create_user(...)

        # --- A CORREÇÃO ESTÁ AQUI ---

        # 2. CRIE UMA CATEGORIA "FALSA" PRIMEIRO
        # (Estou supondo que Categoria tem um campo 'nome')
        self.categoria_teste = Categoria.objects.create(nome='Categoria Teste')

        # 3. PASSE A CATEGORIA AO CRIAR O PRODUTO
        self.produto = Produto.objects.create(
            nome='Sushi Teste',
            preco=10.00,
            descricao='Descricao teste',
            categoria=self.categoria_teste  # <-- A LINHA QUE FALTAVA
        )
        
        # O resto do setUp (URLs) está correto
        self.list_url = reverse('sushiemcasa:listar_produtos')
        self.edit_url = reverse('sushiemcasa:editar_produto', args=[self.produto.pk])

    # ... (o resto dos seus testes 'test_...' não precisa de alteração) ...