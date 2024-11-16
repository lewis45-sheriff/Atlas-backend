from rest_framework import serializers
from .models import Category, Product, User, Order, OrderItem, Subcategory

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username', 'password', 'email']

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
    category_name = serializers.CharField(source='category.name', read_only=True)  # To display the category name

    class Meta:
        model = Product
        fields = ['id', 'name', 'category_name', 'price', 'is_new', 'is_best_seller', 'description', 'avatar']

class ProductDetailSerializer(serializers.ModelSerializer):
    #category_name = CategorySerializer(read_only=True)  # Nested serializer for category details

    class Meta: 
        model = Product
        fields = ['id', 'name','price', 'is_new', 'is_best_seller', 'avatar', 'description', 'stock']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()  # Nesting the ProductSerializer    
    
    
#     [{'product': {'name': 'Jack Daniels', 'price': Decimal('7000.00')}, 'quantity': 1}]
# {'name': 'Jack Daniels', 'price': Decimal('7000.00')}

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'item_subtotal']  # Include item subtotal

class OrderSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    # order_id = serializers.CharField(max_length=255)
    created_at = serializers.DateTimeField()
    status = serializers.CharField(max_length=10)
    products = OrderItemSerializer(many=True)

    def create(self, validated_data):
        print(validated_data)
        products_data = validated_data.pop('products')
        order = Order.objects.create(**validated_data)
        
        print(products_data)

        for item_data in products_data:
            product_id = item_data.get('product_id')  # Expecting product_id in payload
            if not product_id:
                raise serializers.ValidationError("Product ID is required.")
            
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                raise serializers.ValidationError(f"Product with ID {product_id} does not exist.")
            
            OrderItem.objects.create(order=order, product=product, quantity=item_data.get('quantity', 1))

        return order
    
    # def update(self, instance, validated_data):
    #     instance.id = validated_data.get('id', instance.id)
    #     instance.save()
        
    #     return instance
    
    products = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = '__all__'
