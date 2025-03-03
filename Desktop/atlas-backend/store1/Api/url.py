from django.urls import path
from .views import register,  get_products, get_product_by_name,get_order_by_id  ,get_category_products, create_order, get_categories, get_category_subcategories, get_user_orders,auth_user,image_view,get_orders
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', auth_user, name='login'),
    path('product/', get_products, name='Get_product'),
     path('product/<str:product_name>/', get_product_by_name, name='product_by_name'),

    path('create_order/', create_order, name='create_order'),
    path('orders/', get_user_orders, name='get user order'),
    path('categories/', get_categories, name='Get_categories by name'),
    path('categories/<str:name>/', get_category_products, name='get_category_products'),
     path('categories/<str:category_name>/subcategories/', get_category_subcategories, name='category_subcategories'),
    path('categories/<int:category_id>/subcategories/',get_category_subcategories, name='get_category_subcategories'),
    #  path('products/<str:image_name>/', image_view, name='image-view'),
    path ('all_oders', get_orders, name='get all oders'),
    path('all_oders/<int:id>/', get_order_by_id, name='get_order_by_id'),
    path('media/products/<str:image_name>/', image_view, name='image_view'),
  # Corrected the typo and added int parameter
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
