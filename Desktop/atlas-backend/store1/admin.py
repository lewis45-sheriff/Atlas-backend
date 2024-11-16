# admin.py
from django.contrib import admin
from .models import Category, Product, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'image', 'name', 'sub_category', 'price', 'is_new', 'is_best_seller')
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'status', 'user')
    
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'quantity', 'product', 'created_at')
