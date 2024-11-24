import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


# Custom User model extending AbstractUser
class User(AbstractUser):
    middle_name = models.CharField(max_length=150, blank=True, null=True)
    

    def full_name(self):
        return f"{self.first_name} {self.middle_name or ''} {self.last_name}".strip()

    def __str__(self):
        return self.username


# Category model for product categorization
class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# Subcategory model with manual input
class Subcategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="categories", null=True )

    def __str__(self):
        return self.name


# Product model representing items in the store
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products", blank=True, null=True)
    sub_category = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name="products", blank=True, null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    is_new = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    origin = models.CharField(max_length=255, blank=True, null=True)  # Country of origin
    alcohol_content = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)  # Alcohol Content
    brand = models.CharField(max_length=255, blank=True, null=True)  # Brand name

    @property
    def in_stock(self):
        return self.stock > 0

    def __str__(self):
        return self.name


# Order model to track customer orders

class PaymentMethod(models.TextChoices):
    MPESA = 'mpesa', 'M-Pesa'
    PAYPAL = 'paypal', 'PayPal'
    CREDIT_CARD = 'card', 'Credit Card'
    


class Order(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        CONFIRMED = 'confirmed', 'Confirmed'
        SHIPPED = 'shipped', 'Shipped'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'

    id = models.BigAutoField(primary_key=True,null=False)
    order_id = models.CharField(max_length=50, unique=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    status = models.CharField(
        max_length=20, 
        choices=StatusChoices.choices, 
        default=StatusChoices.PENDING
    )
    
    # Billing & Shipping Details
    first_name = models.CharField(max_length=100 ,null=True)
    last_name = models.CharField(max_length=100,null=True)
    email = models.EmailField(max_length= 100, null=True)
    phone_number = models.CharField(max_length=15,null=True)
    location = models.CharField(max_length=255,null=True)
    street_address = models.CharField(max_length=255, blank=True, null=True)
    
    # Payment Details
    payment_method = models.CharField(
        max_length=20, 
        choices=PaymentMethod.choices,
        default=PaymentMethod.MPESA,
    )
    
    # Specific Payment Method Details
    mpesa_phone = models.CharField(max_length=15, blank=True, null=True)
    mpesa_code = models.CharField(max_length=20, blank=True, null=True)
    paypal_email = models.EmailField(blank=True, null=True)
    
    # Financial Details
    subtotal = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    
    # Optional User Association
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        related_name='orders', 
        null=True, 
        blank=True
    )

    def __str__(self):
        return f"Order {self.order_id}"
   
    session_id = models.CharField(max_length=255, null=True, blank=True)  # Optionally store session ID

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='items'
    )
    product = models.ForeignKey(
        'Product', 
        on_delete=models.CASCADE, 
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    created_at =models.DecimalField(max_digits=20, decimal_places=2,null=True)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.order.order_id}"

