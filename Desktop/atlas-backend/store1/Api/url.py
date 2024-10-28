from django.urls import path
from .views import register, login_view, Get_products, get_product_by_id ,get_orders ,get_category_products

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('product/', Get_products, name='Get_product'),  # Add a comma here
    path('product_info/<int:product_id>/', get_product_by_id, name='product_info'),
     path('orders/', get_orders, name='orderlist'),
     path('categories/<str:category_name>/', get_category_products, name='get_category_products'),
  # Corrected the typo and added int parameter
]
