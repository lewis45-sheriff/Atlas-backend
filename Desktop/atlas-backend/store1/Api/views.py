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
    OrderSerializer, CategorySerializer, SubcategorySerializer, serializers, OrderItemSerializer
)

from django.conf import settings
from django.http import HttpResponse, FileResponse
import os
from mimetypes import guess_type
from django.http import FileResponse, JsonResponse
import logging

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
        # Save the Order instance first
        order = serializer.save(user=user)

        # Access the order ID directly from the saved order instance
        order_id = order.order_id

        # Process the products included in the order
        products_data = request.data.get('products', [])
        for item_data in products_data:
            product_name = item_data.get('product')
            quantity = item_data.get('quantity', 1)

            # Validate the product and check stock
            try:
                product = Product.objects.get(name=product_name)  # Fetch product by name
            except Product.DoesNotExist:
                return Response({"error": f"Product with name {product_name} not found."}, status=status.HTTP_404_NOT_FOUND)

            if product.stock < quantity:
                return Response({"error": f"Insufficient stock for {product.name}."}, status=status.HTTP_400_BAD_REQUEST)

            # Reduce stock and save the product
            product.stock -= quantity
            product.save()

            # Create the OrderItem
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=product.price,  # Ensure unit_price is set
                total_price=product.price * quantity
            )

        # Return the response with the order data
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def get_user_orders(request):
    """
    Retrieve orders tied to the authenticated user or based on order_id.
    """
    order_id = request.query_params.get('order_id', None)

    if order_id:
        # Fetch orders associated with the provided order_id
        orders = Order.objects.filter(order_id=order_id)
    elif request.user.is_authenticated:
        # Fetch orders associated with the logged-in user
        orders = Order.objects.filter(user=request.user)
    else:
        # No order_id and user is not authenticated, return error
        return Response({"detail": "Order ID or authenticated user required."}, status=400)

    # Serialize the orders using the OrderSerializer
    serializer = OrderSerializer(orders, many=True)  # Correct usage of the serializer here
    return Response(serializer.data)
@api_view(['GET'])
def get_orders(request):
    """
    Retrieve all orders in the database.
    """
    orders = Order.objects.all()  # Retrieve all orders
    serializer = OrderSerializer(orders, many=True)  # Use the OrderSerializer with many=True
    return Response(serializer.data)


@api_view(['GET'])
def get_order_by_id(request, id):
    """
    Retrieve a specific order by its ID.
    """
    try:
        order = Order.objects.get(id=id)  # Fetch the order by ID
        serializer = OrderSerializer(order)  # Serialize the order
        return Response(serializer.data)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)




logger = logging.getLogger(__name__)

def image_view(request, image_name: str):
    """
    Serve product images from the MEDIA_ROOT/products directory.
    """
    try:
        sanitized_name = os.path.basename(image_name)  # Prevent directory traversal
        image_path = os.path.join(settings.MEDIA_ROOT, 'products', sanitized_name)

        if os.path.exists(image_path):
            content_type, _ = guess_type(image_path)
            content_type = content_type or 'application/octet-stream'

            with open(image_path, 'rb') as img_file:
                return FileResponse(img_file, content_type=content_type)

        logger.warning(f"Image not found: {image_path}")
        return JsonResponse({'error': 'Image not found'}, status=404)

    except Exception as e:
        logger.error(f"Error serving image {image_name}: {e}")
        return JsonResponse({'error': 'An unexpected error occurred'}, status=500)