from rest_framework import serializers
from .models import Category, Product, User, Order, OrderItem, Subcategory

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


# Subcategory Serializer

class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ['id', 'name', 'products']


class CategorySerializer(serializers.ModelSerializer):
    subcategories =SubcategorySerializer(many=True, read_only=True)  # Use the correct argument
    products = serializers.StringRelatedField(many=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'subcategories' ,'products']  # Use the correct field name


# Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    subcategory_name = serializers.CharField(source='sub_category.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'subcategory_name', 'category', 'price', 'is_new', 'is_best_seller', 'description', 'image']


# Product Detail Serializer
class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'category', 'is_new', 'is_best_seller', 'image', 'description', 'stock']


# from rest_framework import serializers

# OrderItem Serializer
class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'unit_price', 'total_price']

# Order Serializer

class OrderSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    # user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)
    firstName = serializers.CharField(write_only=True)
    lastName = serializers.CharField(write_only=True)
    

    
    items = OrderItemSerializer(many=True, required=False)  # Expecting items to be passed in the request

    # Additional fields from the payload
    paymentMethod = serializers.CharField(write_only=True)
    mpesaCode = serializers.CharField(write_only=True, required=False)
    mpesaPhone = serializers.CharField(write_only=True)
    paypalEmail = serializers.EmailField(write_only=True, required=False)
    cardNumber = serializers.CharField(write_only=True, required=False)
    cvv = serializers.CharField(write_only=True, required=False)
    expiryDate = serializers.CharField(write_only=True, required=False)
    
    
    location = serializers.CharField(write_only=True)
    phoneNumber = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'created_at', 'status', 'user', 'items', 'paymentMethod',
            'mpesaCode', 'mpesaPhone', 'paypalEmail', 'cardNumber', 'cvv', 'expiryDate',
            'firstName', 'lastName', 'location', 'phoneNumber', 'email'
        ]
