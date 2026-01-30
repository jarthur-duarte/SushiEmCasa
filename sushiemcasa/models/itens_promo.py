from django.db import models

class BannerPromocional(models.Model):
    """ Model específico para gerenciar os banners do carrossel de ofertas. """
    titulo = models.CharField(max_length=100, verbose_name="Título da Promoção")
    descricao = models.TextField(verbose_name="Descrição Curta")
    imagem = models.ImageField(upload_to='banners/', verbose_name="Imagem do Banner (Recomendado: 1200x400)")
    
    produto_vinculado = models.ForeignKey(
        'Produto', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Produto para Venda",
        help_text="Selecione o produto que será adicionado ao carrinho quando clicarem no banner."
    )
    
    preco_promocional = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Preço de Oferta")
    preco_antigo = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, verbose_name="Preço Riscado")
    
    ativo = models.BooleanField(default=True, verbose_name="Banner Ativo?")
    ordem = models.PositiveIntegerField(default=0, verbose_name="Ordem de Exibição")

    class Meta:
        verbose_name = "Banner Promocional"
        verbose_name_plural = "Banners Promocionais"
        ordering = ['ordem']

    def __str__(self):
        return self.titulo