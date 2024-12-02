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


# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubcategorySerializer(many=True, read_only=True)
    products = serializers.StringRelatedField(many=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'subcategories', 'products']


# Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    subcategory_name = serializers.CharField(source='sub_category.name', read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'price', 'is_new', 'is_best_seller', 
            'description', 'image', 'subcategory_name', 'image_url'
        ]

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


# Product Detail Serializer
class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'price', 'category', 'is_new', 'is_best_seller',
            'image', 'description', 'stock', 'alcohol_content', 'origin'
        ]


# OrderItem Serializer
class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.CharField()  # Accept product names

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'unit_price', 'total_price']

class OrderSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    order_id = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    username = serializers.CharField( read_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    street_address = serializers.CharField(write_only=True)
    location = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    payment_method = serializers.CharField(write_only=True)
    mpesa_code = serializers.CharField(write_only=True, required=False)
    mpesa_phone = serializers.CharField(write_only=True)
    total = serializers.CharField(write_only=True)
    products = OrderItemSerializer(many=True, write_only=True)
    items = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = [
            'id','order_id', 'username', 'created_at', 'status', 'first_name', 'last_name',
            'street_address', 'location', 'phone_number', 'email', 'payment_method',
            'mpesa_code', 'mpesa_phone', 'products', 'items', 'total'
        ]

    def get_items(self, obj):
        order_items = OrderItem.objects.filter(order=obj)
        return OrderItemSerializer(order_items, many=True).data

    def create(self, validated_data):
        # Extract products and additional fields
        products_data = validated_data.pop('products', [])
        user = validated_data.pop('user', None)

        # Create the Order instance
        order = Order.objects.create(user=user, **validated_data)

        # Process each product item
        for item_data in products_data:
            product_name = item_data.get('product')
            quantity = item_data.get('quantity', 1)

            try:
                product = Product.objects.get(name=product_name)
            except Product.DoesNotExist:
                raise serializers.ValidationError({
                    'product': f"Product with name '{product_name}' does not exist."
                })

            if product.stock < quantity:
                raise serializers.ValidationError({
                    'product': f"Insufficient stock for product '{product_name}'."
                })

            product.stock -= quantity
            product.save()

            unit_price = product.price
            total_price = unit_price * quantity

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price
            )

        return order
# Image Upload Serializer
class ImageUploadSerializer(serializers.Serializer):
    image = serializers.ImageField()
