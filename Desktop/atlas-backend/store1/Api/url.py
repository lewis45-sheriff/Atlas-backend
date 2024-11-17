from django.urls import path
from .views import register, login_view, Get_products, get_product_by_id ,get_orders ,get_category_products, create_order, Get_categories, get_category_subcategories

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('product/', Get_products, name='Get_product'),
    path('product_info/<int:product_id>/', get_product_by_id, name='product_info'),
    path('create_order/', create_order, name='create_order'),
    path('orders/', get_orders, name='orderlist'),
    path('category/', Get_categories, name='Get_categories by name'),
    path('categories/<int:id>/<str:type>', get_category_products, name='get_category_products'),
    path('category/<int:category_id>/subcategories/',get_category_subcategories, name='get_category_subcategories'),
  # Corrected the typo and added int parameter
]
