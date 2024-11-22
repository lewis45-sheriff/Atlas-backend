from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import authenticate, get_user_model
from store1.models import Product, Order, Category, Subcategory, OrderItem
from ..serializers import (
    UserSerializer, ProductSerializer, ProductDetailSerializer,
    OrderSerializer, CategorySerializer, SubcategorySerializer ,serializers
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
        
        
        user = serializer.save()
        token = Token.objects.create(user=user)
        return Response({
            'success': True,
            'message': 'User registered successfully',
            'token': token.key
        }, status=status.HTTP_201_CREATED)

    


# @api_view(['POST'])
# def login_view(request):
#     """Log in a user and return their authentication token."""
#     username = request.data.get('username')
#     password = request.data.get('password')
#     user = authenticate(request, username=username, password=password)

#     if user:
#         token, _ = Token.objects.get_or_create(user=user)
#         return Response({
#             "message": "Login successful!",
#             "token": token.key
#         }, status=status.HTTP_200_OK)

#     return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def authUser(request):
    """Authenticate the user and return the token."""
    username = request.data.get('username')
    password = request.data.get('password')

    if username and password:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'message': "Incorrect login credentials"}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate the user
        user_auth = authenticate(username=username, password=password)

        if user_auth is not None:
            # Create access and refresh tokens for the authenticated user
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # Return user data along with access and refresh tokens
            serializer = UserSerializer(user)  # Use UserSerializer for user data serialization
            data = serializer.data
            data['access'] = access_token
            data['refresh'] = str(refresh)

            # Ensure token is included as part of response body
            return Response({
                'message': 'Login successful',
                'data': data
            }, status=status.HTTP_200_OK)

        return Response({'message': "Incorrect login credentials"}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'message': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

# def _create_response(self, status_code, message, entity=None):
#     response = ApiResponse()  # Assuming ApiResponse is a custom class you're using for API response formatting
#     response.setStatusCode(status_code)
#     response.setMessage(message)
#     if entity:
#         response.setEntity(entity)
#     return Response(response.toDict(), status=status_code)


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
    
    # Check if the user is authenticated, if not, assign an anonymous user (guest user)
    user = request.user if request.user.is_authenticated else None  # None allows anonymous orders
    
    # Add the user to the request data if it's not already present (for serializer validation)
    request.data['user'] = user

    # Use the OrderSerializer to validate and save the order
    serializer = OrderSerializer(data=request.data)
    if serializer.is_valid():
        # Save the order with the user (authenticated or anonymous)
        order = serializer.save(user=user)

        # Process the products and create order items
        products_data = request.data.get('products', [])
        for item_data in products_data:
            product_id = item_data['product']
            quantity = item_data.get('quantity', 1)

            # Ensure price and quantity are valid numbers
            price = item_data.get('price')
            if price is None:
                raise serializers.ValidationError("Price is required for all products.")
            
            if quantity is None or quantity <= 0:
                raise serializers.ValidationError(f"Invalid quantity for product {product_id}.")

            # Fetch the product instance from the database
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({"error": f"Product with ID {product_id} not found."}, status=status.HTTP_404_NOT_FOUND)

            # Validate stock
            if product.stock is None or product.stock < quantity:
                return Response({"error": f"Insufficient stock for product {product.name}."}, status=status.HTTP_400_BAD_REQUEST)

            # Reduce stock and create the order item
            product.stock -= quantity
            product.save()

            # Create OrderItem instance
            OrderItem.objects.create(order=order, product=product, quantity=quantity)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # Return validation errors if any
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_orders(request):
    """Retrieve all orders for the logged-in user."""
    # Filter orders for the specific user
    orders = Order.objects.filter(user=request.user)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)
