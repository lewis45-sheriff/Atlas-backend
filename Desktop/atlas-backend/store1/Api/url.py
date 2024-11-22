from django.urls import path
from .views import register,  Get_Products, get_product_by_name ,get_orders ,get_category_products, create_order, get_categories, get_category_subcategories, get_user_orders,authUser

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', authUser, name='login'),
    path('product/', Get_Products, name='Get_product'),
     path('product/<str:product_name>/', get_product_by_name, name='product_by_name'),

    path('create_order/', create_order, name='create_order'),
    path('orders/', get_user_orders, name='get user order'),
    path('categories/', get_categories, name='Get_categories by name'),
    path('categories/<str:name>/', get_category_products, name='get_category_products'),
     path('categories/<str:category_name>/subcategories/', get_category_subcategories, name='category_subcategories'),
    path('categories/<int:category_id>/subcategories/',get_category_subcategories, name='get_category_subcategories'),
  # Corrected the typo and added int parameter
]
