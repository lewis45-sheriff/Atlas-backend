from rest_framework import serializers
from .models import Category, Product, User, Order, OrderItem, Subcategory

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email']

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ['id', 'name']


class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, read_only=True)  # Reverse relationship

    class Meta:
        model = Category
        fields = ['id', 'name', 'subcategories']


class ProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    subcategory_name = serializers.CharField(source='sub_category.name', read_only=True)  # To display the subcategory name

    class Meta:
        model = Product
        fields = ['id', 'name', 'subcategory_name', 'price', 'is_new', 'is_best_seller', 'description', 'avatar']


class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'is_new', 'is_best_seller', 'avatar', 'description', 'stock']


class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product", write_only=True
    )  # Allow passing product ID when creating an order
    product = ProductSerializer(read_only=True)  # Display product details in response

    class Meta:
        model = OrderItem
        fields = ['product', 'product_id', 'quantity', 'item_subtotal']  # Include item subtotal


class OrderSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    products = OrderItemSerializer(many=True, write_only=True)  # Allow passing products during creation
    items = OrderItemSerializer(many=True, read_only=True, source="orderitem_set")  # Display related items

    class Meta:
        model = Order
        fields = ['id', 'order_id', 'created_at', 'status', 'user', 'products', 'items']

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        order = Order.objects.create(**validated_data)

        for item_data in products_data:
            product = item_data['product']
            quantity = item_data.get('quantity', 1)

            # Validate stock
            if product.stock < quantity:
                raise serializers.ValidationError(
                    f"Insufficient stock for product {product.name}."
                )

            # Reduce stock and create order item
            product.stock -= quantity
            product.save()
            OrderItem.objects.create(order=order, product=product, quantity=quantity)

        return order
