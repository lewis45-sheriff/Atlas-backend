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


# Order Item Serializer 
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['product', 'product_name', 'product_price', 'quantity']




# Order Serializer
class OrderSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=False)
    products = OrderItemSerializer(many=True)  # Handle multiple products
    items = OrderItemSerializer(many=True, read_only=True, source="orderitem_set")  # Return order items for the order

    class Meta:
        model = Order
        fields = ['id', 'order_id', 'created_at', 'status', 'user', 'products', 'items']

    def create(self, validated_data):
        # Extract product data from validated data
        products_data = validated_data.pop('products')

        # Get the user (if provided, else None for guest users)
        user = validated_data.get('user', None)

        # Create the Order instance
        order = Order.objects.create(**validated_data)

        # Process each product and create associated OrderItems
        for item_data in products_data:
            product = item_data['product']
            quantity = item_data.get('quantity', 1)

            # Validate product stock
            if product.stock < quantity:
                raise serializers.ValidationError(
                    f"Insufficient stock for product {product.name}."
                )

            # Reduce stock and create the OrderItem
            product.stock -= quantity
            product.save()

            # Create OrderItem instance
            OrderItem.objects.create(order=order, product=product, quantity=quantity)

        return order
