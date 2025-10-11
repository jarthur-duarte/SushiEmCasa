from django.db import models
from django.contrib.auth.models import User



class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('In Preparation', 'In Preparation'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


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
        return f"{self.quantity}x {self.item_name} (Order #{self.order.id})"