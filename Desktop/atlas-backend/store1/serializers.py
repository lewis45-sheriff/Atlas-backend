from rest_framework import serializers
from .models import Category, Product, User, Order, OrderItem

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'category_name']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)  # To display the category name

    class Meta:
        model = Product
        fields = ['id', 'name', 'category_name', 'price', 'is_new', 'is_best_seller', 'description', 'avatar']

class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)  # Nested serializer for category details

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'price', 'is_new', 'is_best_seller', 'avatar', 'description', 'stock']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()  # Nesting the ProductSerializer

    class Meta:
        model = OrderItem
        fields = ('product', 'quantity', 'item_subtotal')  # Include item subtotal

class OrderSerializer(serializers.ModelSerializer):
    products = OrderItemSerializer(many=True)  # Nesting OrderItemSerializer

    class Meta:
        model = Order
        fields = ('order_id', 'created_at', 'status', 'products', 'user')  # Include user if needed

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        order = Order.objects.create(**validated_data)
        for item_data in products_data:
            product_data = item_data.pop('product')
            product = Product.objects.get(id=product_data['id'])  # Fetch the product instance
            OrderItem.objects.create(order=order, product=product, **item_data)
        return order
