from django.db import models

class BannerPromocional(models.Model):
    """ Model específico para gerenciar os banners do carrossel de ofertas. """
    titulo = models.CharField(max_length=100, verbose_name="Special title")
    descricao = models.TextField(verbose_name="Short description")
    imagem = models.ImageField(upload_to='banners/', verbose_name="Banner image (recommended: 1200x400)")
    
    produto_vinculado = models.ForeignKey(
        'Produto', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Product for sale",
        help_text="Select the product added to the cart when someone clicks the banner."
    )
    
    preco_promocional = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Deal price")
    preco_antigo = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, verbose_name="Original price (crossed out)")
    
    ativo = models.BooleanField(default=True, verbose_name="Active?")
    ordem = models.PositiveIntegerField(default=0, verbose_name="Display order")

    class Meta:
        verbose_name = "Promo banner"
        verbose_name_plural = "Promo banners"
        ordering = ['ordem']

    def __str__(self):
        return self.titulo