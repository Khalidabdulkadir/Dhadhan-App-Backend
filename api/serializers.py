
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Category, Product, Order, OrderItem, Reel, SavedReel, Restaurant

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['username'] = validated_data['email']
        user = User.objects.create_user(**validated_data)
        return user

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    restaurant = serializers.PrimaryKeyRelatedField(queryset=Restaurant.objects.all(), required=False, allow_null=True)
    restaurant_data = RestaurantSerializer(source='restaurant', read_only=True)
    
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    discounted_price = serializers.ReadOnlyField()
    restaurant = serializers.PrimaryKeyRelatedField(queryset=Restaurant.objects.all(), required=False, allow_null=True)
    restaurant_data = RestaurantSerializer(source='restaurant', read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'image', 'category', 'rating', 'is_hot', 'is_promoted', 'discount_percentage', 'discounted_price', 'shipping_fee', 'restaurant', 'restaurant_data']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['discount_percentage'] = instance.effective_discount_percentage
        return representation

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    product_image = serializers.ImageField(source='product.image', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_image', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['user', 'total_amount', 'status', 'created_at']

class CreateOrderSerializer(serializers.Serializer):
    items = serializers.ListField(child=serializers.DictField(child=serializers.IntegerField()))
    delivery_address = serializers.CharField(required=False, allow_blank=True)
    payment_method = serializers.CharField()
    phone_number = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        phone_number = validated_data.pop('phone_number', None)
        user = self.context['request'].user
        
        # Calculate total
        total = 0
        order_items = []
        
        for item in items_data:
            product = Product.objects.get(id=item['id'])
            quantity = item['quantity']
            # Use discounted price
            price_per_unit = product.discounted_price
            price = price_per_unit * quantity
            total += price
            order_items.append({
                'product': product,
                'quantity': quantity,
                'price': price_per_unit
            })
            
        # Add delivery fee if applicable
        if validated_data.get('delivery_address') and validated_data.get('delivery_address') != 'Pickup':
            total += 500 # 500 KES delivery fee
            
        # Create Order
        order = Order.objects.create(
            user=user,
            total_amount=total,
            **validated_data
        )
        
        # Create Order Items
        for item in order_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['price']
            )

        # Handle M-Pesa Payment
        if validated_data.get('payment_method') == 'mpesa' and phone_number:
            try:
                from api.utils import IntaSendService
                service = IntaSendService()
                response = service.trigger_stk_push(
                    phone_number=phone_number,
                    amount=float(total),
                    narrative=f"Order {order.id}"
                )
            except Exception as e:
                print(f"Payment Error: {str(e)}")
            
        return order

class ReelSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source='product', read_only=True)
    is_saved = serializers.SerializerMethodField()
    restaurant = serializers.PrimaryKeyRelatedField(queryset=Restaurant.objects.all(), required=False, allow_null=True)
    restaurant_data = RestaurantSerializer(source='restaurant', read_only=True)

    class Meta:
        model = Reel
        model = Reel
        fields = ['id', 'product', 'product_details', 'video', 'caption', 'is_highlight', 'views', 'created_at', 'is_saved', 'restaurant', 'restaurant_data']

    def get_is_saved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return SavedReel.objects.filter(user=request.user, reel=obj).exists()
        return False

class SavedReelSerializer(serializers.ModelSerializer):
    reel_details = ReelSerializer(source='reel', read_only=True)
    
    class Meta:
        model = SavedReel
        fields = ['id', 'user', 'reel', 'reel_details', 'saved_at']
        read_only_fields = ['user', 'saved_at']
