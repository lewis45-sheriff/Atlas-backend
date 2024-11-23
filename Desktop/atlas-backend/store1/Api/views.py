from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from store1.models import Product, Order, Category, Subcategory, OrderItem
from ..serializers import (
    UserSerializer, ProductSerializer, ProductDetailSerializer,
    OrderSerializer, CategorySerializer, SubcategorySerializer, serializers
)

from django.conf import settings
from django.http import HttpResponse, FileResponse
import os

User = get_user_model()

### User Authentication Endpoints ###

@permission_classes([AllowAny])
@api_view(['POST'])
def register(request):
    """
    Register a new user and generate an authentication token.
    """
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token = RefreshToken.for_user(user)
        return Response({
            'success': True,
            'message': 'User registered successfully',
            'access': str(token.access_token),
            'refresh': str(token),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def auth_user(request):
    """
    Authenticate the user and return access and refresh tokens.
    """
    username = request.data.get('username')
    password = request.data.get('password')

    if username and password:
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            serializer = UserSerializer(user)
            return Response({
                'message': 'Login successful',
                'user': serializer.data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_200_OK)
        return Response({'error': "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)


### Product Endpoints ###

@api_view(['GET'])
def get_products(request):
    """
    Retrieve all products.
    """
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_product_by_name(request, product_name):
    """
    Retrieve a product by its name.
    """
    product = Product.objects.filter(name=product_name).first()
    if not product:
        raise NotFound(f"Product with name '{product_name}' not found.")
    serializer = ProductDetailSerializer(product)
    return Response(serializer.data)


@api_view(['GET'])
def get_category_products(request, name, type=None):
    """
    Retrieve products by category and optional type (e.g., best seller, new arrivals).
    """
    products = Product.objects.filter(category__name=name)
    if type == 'is_best_seller':
        products = products.filter(is_best_seller=True)
    elif type == 'is_new':
        products = products.filter(is_new=True)

    if not products.exists():
        return Response({"message": "No products found for this category."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


### Category Endpoints ###

@api_view(['GET'])
def get_categories(request):
    """
    Retrieve all categories or filter by name, including nested subcategories and products.
    """
    name = request.query_params.get('name')
    categories = Category.objects.filter(name__icontains=name) if name else Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_category_subcategories(request, category_name):
    """
    Retrieve subcategories and their products for a given category.
    """
    category = Category.objects.filter(name=category_name).first()
    if not category:
        raise NotFound(f"Category with name '{category_name}' not found.")
    subcategories = category.subcategory_set.all()

    response_data = [
        {
            'subcategory': SubcategorySerializer(subcategory).data,
            'products': ProductSerializer(Product.objects.filter(sub_category=subcategory), many=True).data,
        }
        for subcategory in subcategories
    ]
    return Response(response_data)


### Order Endpoints ###

@api_view(['POST'])
@permission_classes([AllowAny])
def create_order(request):
    """
    Create a new order. Anonymous users are allowed.
    """
    user = request.user if request.user.is_authenticated else None
    serializer = OrderSerializer(data=request.data)
    if serializer.is_valid():
        order = serializer.save(user=user)

        # Process the products included in the order
        products_data = request.data.get('products', [])
        for item_data in products_data:
            product_id = item_data.get('product')
            quantity = item_data.get('quantity', 1)

            # Validate the product and check stock
            try:
                product = Product.objects.get(name=get_product_by_name)
            except Product.DoesNotExist:
                return Response({"error": f"Product with ID {get_product_by_name} not found."}, status=status.HTTP_404_NOT_FOUND)

            if product.stock < quantity:
                return Response({"error": f"Insufficient stock for {product.name}."}, status=status.HTTP_400_BAD_REQUEST)

            # Reduce stock and save the product
            product.stock -= quantity
            product.save()

            # Create the OrderItem with unit_price set explicitly
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                  # Ensure this is set
            )

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
  # Only authenticated users can access their orders
def get_user_orders(request):
    """
    Retrieve orders tied to the authenticated user.
    """
    orders = Order.objects.filter(user=request.user)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])

def get_orders(request):
    """
    Retrieve all orders for the authenticated user.
    """
    orders = Order.objects.filter(user=request.user)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

def image_view(request, image_name):
    # Get the path to the image file
    image_path = os.path.join(settings.MEDIA_ROOT, 'products', image_name)

    if os.path.exists(image_path):
        return FileResponse(open(image_path, 'rb'), content_type='image/jpeg')
    else:
        return HttpResponse("Image not found", status=404)
