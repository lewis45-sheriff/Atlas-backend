from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotFound

from django.contrib.auth import authenticate, get_user_model
from store1.models import Product, Order, Category, Subcategory
from ..serializers import (
    UserSerializer, ProductSerializer, ProductDetailSerializer,
    OrderSerializer, CategorySerializer, SubcategorySerializer
)

User = get_user_model()

# User Authentication
@permission_classes([AllowAny])
@api_view(['POST'])
def register(request):
    """Register a new user and generate an authentication token."""
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")
        
        if User.objects.filter(username=username).exists():
            return Response({'success': False, 'message': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({"success": False, "message": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        token = Token.objects.create(user=user)
        return Response({
            'success': True,
            'message': 'User registered successfully',
            'token': token.key
        }, status=status.HTTP_201_CREATED)

    return Response({'success': False, 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_view(request):
    """Log in a user and return their authentication token."""
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)

    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "message": "Login successful!",
            "token": token.key
        }, status=status.HTTP_200_OK)

    return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


# Product Endpoints
@api_view(['GET'])
def Get_Products(request):
    """Retrieve all products."""
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_product_by_name(request, product_name):
    """Retrieve a product by its name."""
    # Get the product by its name
    product = Product.objects.filter(name=product_name).first()

    if not product:
        raise NotFound(f"Product with name '{product_name}' not found.")

    # Serialize the product data
    serializer = ProductDetailSerializer(product)
    return Response(serializer.data)


@api_view(['GET'])
def get_category_products(request, name, type=None):
    """Retrieve products by category and optional type."""
    products = Product.objects.filter(category__name=name)

    # Optional filters
    if type == 'is_best_seller':
        products = products.filter(is_best_seller=True)
    elif type == 'is_new':
        products = products.filter(is_new=True)

    if not products.exists():
        return Response({"message": "No products found for this category."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


# Category Endpoints
@api_view(['GET'])
def get_categories(request):
    """Retrieve all categories or filter by name and include subcategories and products."""
    name = request.query_params.get('name', None)

    # Filter categories based on name if provided, otherwise return all
    categories = Category.objects.filter(name__icontains=name) if name else Category.objects.all()

    # Serialize the categories with nested subcategories and products
    serializer = CategorySerializer(categories, many=True)

    # Return the response with category data, subcategories, and nested product data
    return Response(serializer.data)


@api_view(['GET'])
def get_category_subcategories(request, category_name):
    """Retrieve subcategories and their products for a given category by name."""

    # Get the category by its name
    category = Category.objects.filter(name=category_name).first()

    if not category:
        raise NotFound(f"Category with name '{category_name}' not found.")

    # Get all subcategories for this category
    subcategories = category.subcategory_set.all()

    # Prepare the response data with subcategories and products
    subcategory_data = [
        {
            'sub_category': SubcategorySerializer(subcategory).data,
            'products': ProductSerializer(Product.objects.filter(sub_category=subcategory), many=True).data
        }
        for subcategory in subcategories
    ]

    return Response(subcategory_data)


# Order Endpoints
@api_view(['GET'])
def get_user_orders(request):
    """Retrieve orders tied to the authenticated user."""
    orders = Order.objects.filter(user=request.user)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['POST', 'GET'])
def create_order(request):
    """Create a new order."""
    serializer = OrderSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)  # Save the order with the authenticated user
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_orders(request):
    """Retrieve all orders for the logged-in user."""
    # Filter orders for the specific user
    orders = Order.objects.filter(user=request.user)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)
