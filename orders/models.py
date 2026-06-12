from django.db import models
from django.contrib.auth.models import User


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('paid',      'Paid'),
        ('processing','Processing'),
        ('shipped',   'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('failed',    'Failed'),
    ]

    user           = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    name           = models.CharField(max_length=200)
    phone          = models.CharField(max_length=20)
    address        = models.TextField()
    total_price    = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=150, blank=True, null=True, unique=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.id} — {self.user.username}'

    def get_item_count(self):
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    order    = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product  = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField()
    price    = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        name = self.product.name if self.product else 'Deleted product'
        return f'{name} × {self.quantity}'

    def get_subtotal(self):
        return self.price * self.quantity