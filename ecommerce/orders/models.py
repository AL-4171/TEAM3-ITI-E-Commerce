# Create your models here.
from django.conf import settings
from django.db import models
 
from catalog.models import Product
 
 
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
 
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
 
    # Shipping info (project spec item #43)
    shipping_full_name = models.CharField(max_length=150)
    shipping_phone = models.CharField(max_length=11)
    shipping_address = models.CharField(max_length=255)
    shipping_city = models.CharField(max_length=100)
 
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        ordering = ['-created_at']
 
    def __str__(self):
        return f"Order #{self.id} - {self.user.email}"
 
 
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    # PROTECT: prevents deleting a product that already appears in
    # someone's order history.
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField()
 
    # Snapshot of price at time of purchase — keeps order history accurate
    # even if the product's price changes later (project spec item #53).
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
 
    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order #{self.order.id})"
 
    def subtotal(self):
        return self.quantity * self.price_at_purchase
 