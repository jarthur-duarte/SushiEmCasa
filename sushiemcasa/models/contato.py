# sushiemcasa/models.py
from django.db import models

class MensagemFeedback(models.Model):
    nome = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    mensagem = models.TextField()
    data_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mensagem de {self.nome or 'Anônimo'}"

# Se você tiver outros modelos (como Pedido, Produto), eles também virão para este arquivo.