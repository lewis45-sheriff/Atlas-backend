from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate, get_user_model
from django.http import Http404
from ..serializers import UserSerializer, ProductSerializer, ProductDetailSerializer ,OrderSerializer
from rest_framework.authtoken.models import Token
from store1.models import Product ,Order

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

@api_view(['POST'])
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
    return Response(serializer.data)  #