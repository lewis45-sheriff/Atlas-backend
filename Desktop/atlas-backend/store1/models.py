import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

# Custom User model extending AbstractUser
class User(AbstractUser):
    middle_name = models.CharField(max_length=150, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)

    def full_name(self):
        return f"{self.first_name} {self.middle_name or ''} {self.last_name}".strip()

    def __str__(self):
        return self.username


    
# Category model for product categorization
class Category(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name
    
class Subcategory(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories", null=True, blank=True)

    def __str__(self):
        return self.name
# models.py



# Product model representing items in the store
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    # category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    sub_category = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name="products", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    is_new = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.jpg', blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    @property
    def in_stock(self):
        return self.stock > 0

    def __str__(self):
        return self.name

# Order model representing a customer's order
class Order(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'
    
    id = models.BigAutoField(primary_key=True)
    order_id = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    products = models.ManyToManyField(Product, through="OrderItem", related_name="orders")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders", null= True, blank=True)

    def __str__(self):
        return f"Order {self.order_id}"

# OrderItem model to track product quantities in each order
class OrderItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(default=datetime.datetime.now)

    @property
    def item_subtotal(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.product.name} in order {self.order.order_id}"
