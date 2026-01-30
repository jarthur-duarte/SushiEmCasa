from django.db import models

class Categoria(models.Model):
    """ Define uma categoria para filtrar o cardápio (ex: Temaki, Combinado). """
    nome = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True) 

    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name_plural = "Categorias"
        verbose_name = "Categoria"


class Produto(models.Model):
    """ Define a estrutura de um produto de sushi no cardápio. """
    disponivel = models.BooleanField(default=True)
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
        return f"{self.nome} ({self.categoria.nome})" 
    
    class Meta:
        verbose_name_plural = "Produtos"
        verbose_name = "Produto"

