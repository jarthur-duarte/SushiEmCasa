from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
from django.core.exceptions import ValidationError

class Order(models.Model):
    STATUS_CHOICES = (
        ('pendente', 'Pending'),      
        ('preparando', 'Preparing'),  
        ('saiu_entrega', 'Out for Delivery'), 
        ('entregue', 'Delivered'),    
        ('cancelado', 'Canceled'),    
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    delivery_datetime = models.DateTimeField(
        verbose_name="Delivery Date and Time",
        null=True,
        blank=True
    )

    def __str__(self):
        if self.user:
            nome_cliente = self.user.username
        else:
            nome_cliente = "Convidado (Sem Login)"
            
        return f"Order #{self.id} - {nome_cliente}"
    
    def clean(self):
        if not self.id and self.delivery_datetime:
            now_plus_24h = timezone.now() + datetime.timedelta(hours=24)
            if timezone.is_naive(self.delivery_datetime):  
                delivery_dt_aware = timezone.make_aware(self.delivery_datetime, timezone.get_current_timezone())
            else:
                delivery_dt_aware = self.delivery_datetime
            if delivery_dt_aware < now_plus_24h:
                raise ValidationError({'delivery_datetime': 'Delivery date and time must be at least 24 hours in advance.'})

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    
    produto = models.ForeignKey(
        'sushiemcasa.Produto', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='order_items'
    ) 
    item_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        product_name = self.produto.nome if self.produto else self.item_name
        return f"{self.quantity}x {self.item_name} (Order #{self.order.id})"