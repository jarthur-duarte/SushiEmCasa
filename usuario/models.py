from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class Order(models.Model):
    STATUS_CHOICES = (
        ('Pendente', 'Pendente'),
        ('Em preparo', 'Em preparo'),
        ('A caminho', 'A caminho'),
        ('Entregue', 'Entregue'),
        ('Cancelado', 'Cancelado'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pendente')

    def __str__(self):
        return f"Pedido #{self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    item_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.item_name} (Pedido #{self.order.id})"
