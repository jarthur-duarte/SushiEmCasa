# sushiemcasa/models/produtos.py
from django.db import models

# NOVO MODELO: Categoria
class Categoria(models.Model):
    """ Define uma categoria para filtrar o cardápio (ex: Temaki, Combinado). """
    nome = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True) # URL amigável

    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name_plural = "Categorias"
        verbose_name = "Categoria"


# MODELO EXISTENTE: Produto
class Produto(models.Model):
    """ Define a estrutura de um produto de sushi no cardápio. """
    
    # CHAVE ESTRANGEIRA ADICIONADA: Linka o produto a uma categoria
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.CASCADE, 
        related_name='produtos'
    )

    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=6, decimal_places=2)
    imagem = models.ImageField(upload_to='produtos/') 

    def __str__(self):
        # Agora mostra a categoria no Admin também
        return f"{self.nome} ({self.categoria.nome})" 
    
    class Meta:
        verbose_name_plural = "Produtos"
        verbose_name = "Produto"

# Remova quaisquer classes Order ou OrderItem que possam ter sido duplicadas aqui!