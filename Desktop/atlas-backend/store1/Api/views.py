from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate, get_user_model
from django.http import Http404
from ..serializers import UserSerializer, ProductSerializer, ProductDetailSerializer, OrderSerializer, CategorySerializer, SubCategorySerializer
from rest_framework.authtoken.models import Token
from store1.models import Product, Order, Category
from django.shortcuts import get_object_or_404
from rest_framework.parsers import JSONParser
from io import BytesIO
import json

User = get_user_model()

@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data=request.data)
    
    if serializer.is_valid():
        # Check if the username already exists
        if User.objects.filter(username=serializer.validated_data['username']).exists():
            return Response({'success': False, 'message': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        return Response({'success': True, 'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
    
    return Response({'success': False, 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST','GET'])
def login_view(request):
    username = request.data.get('username')  # Use username instead of email
    password = request.data.get('password')

    user = authenticate(request, username=username, password=password)

    if user is not None:
        token, created = Token.objects.get_or_create(user=user)  # Get or create a token
        return Response({"message": "Login successful!", "token": token.key}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def Get_products(request):
    products = Product.objects.all()  # Use a lowercase variable for the queryset
    serializer = ProductSerializer(products, many=True)  # Serialize the queryset
    return Response(serializer.data)  # Return serialized data

@api_view(['GET'])
def get_product_by_id(request, product_id):
    try:
        product = Product.objects.get(id=product_id)  # Retrieve the product by ID
        serializer = ProductDetailSerializer(product)  # Use serializer for detailed response
        return Response(serializer.data)  # Return serialized product data
    except Product.DoesNotExist:
        raise Http404("Product not found")  # Handle case where product doesn't exist

@api_view(['GET'])
def get_orders(request):
    orders = Order.objects.all()  # Retrieve all orders
    serializer = OrderSerializer(orders, many=True)  # Serialize the queryset
    return Response(serializer.data)  

@api_view(['GET'])
def get_category_products(request, id, type=None):
    """
    Retrieve products by category and optional type.
    """
    products = Product.objects.filter(sub_category__id=id)

    # Filter by optional type
    if type == 'is_best_seller':
        products = products.filter(is_best_seller=True)
    elif type == 'is_new':
        products = products.filter(is_new=True)

    if not products.exists():
        return Response({"message": "No products found for this category."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def Get_categories(request):
    name = request.query_params.get('name', None)  # Get the 'name' query parameter
    if name:
        categories = Category.objects.filter(name__icontains=name)  # Filter categories by name
    else:
        categories = Category.objects.all()  # If no 'name' parameter, get all categories
    
    serializer = CategorySerializer(categories, many=True)  # Serialize the queryset
    return Response(serializer.data)  # Return serialized data

@api_view(['GET'])
def get_category_subcategories(request, category_id):
    """
    Retrieve subcategories for a given category, including products in each subcategory.
    """
    category = get_object_or_404(Category, id=category_id)
    subcategories = category.subcategories.all()  # Reverse relationship
    
    subcategory_data = []
    
    for subcategory in subcategories:
        # Get products associated with each subcategory
        products = Product.objects.filter(sub_category=subcategory)
        product_serializer = ProductSerializer(products, many=True)  # Serialize products
        
        # Add products to the subcategory data
        subcategory_data.append({
            'sub_category': SubCategorySerializer(subcategory).data,
            'products': product_serializer.data
        })
    
    return Response(subcategory_data)


@api_view(['POST', 'GET'])
def create_order(request):
    if request.method == 'POST':
        # Ensure the user is passed in the request
        user = request.data.get('user')  # Expect user ID to be provided in the request
        
        # Ensure that user exists
        if not user:
            return Response({"error": "User is required to create an order."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_instance = User.objects.get(id=user)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_400_BAD_REQUEST)

        # Proceed with deserializing the order data
        json_data = json.dumps(request.data)
        byte_data = json_data.encode('utf-8')
        stream = BytesIO(byte_data)

        # Deserialize the data
        data = JSONParser().parse(stream)
        data['user'] = user_instance.id  # Add user information to the order data

        serializer = OrderSerializer(data=data)

        if serializer.is_valid():
            # Save the order with user information
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
