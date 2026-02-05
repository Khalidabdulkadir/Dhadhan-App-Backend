
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Category, Product, Order, OrderItem, Reel, SavedReel, Restaurant, ProductVariant, ProductAddOn

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

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'name', 'price', 'is_default']

class ProductAddOnSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAddOn
        fields = ['id', 'name', 'price', 'is_available']

class ProductSerializer(serializers.ModelSerializer):
    discounted_price = serializers.ReadOnlyField()
    restaurant = serializers.PrimaryKeyRelatedField(queryset=Restaurant.objects.all(), required=False, allow_null=True)
    restaurant_data = RestaurantSerializer(source='restaurant', read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    addons = ProductAddOnSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'image', 'category', 'rating', 'is_hot', 
                 'is_promoted', 'discount_percentage', 'discounted_price', 'restaurant', 
                 'restaurant_data', 'variants', 'addons']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['discount_percentage'] = instance.effective_discount_percentage
        return representation

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    product_image = serializers.ImageField(source='product.image', read_only=True)
    variant_name = serializers.CharField(source='variant.name', read_only=True)
    addons_names = serializers.StringRelatedField(source='addons', many=True, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_image', 'quantity', 'price', 'variant_name', 'addons_names']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['user', 'total_amount', 'status', 'created_at']

class CreateOrderSerializer(serializers.Serializer):
    items = serializers.ListField(child=serializers.DictField())  # Changed to DictField for flexibility
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
            variant_id = item.get('variant_id')
            addon_ids = item.get('addon_ids', [])
            
            # Determine Base Price
            variant = None
            if variant_id:
                variant = ProductVariant.objects.get(id=variant_id)
                base_price = variant.price
            else:
                base_price = product.discounted_price
                
            # Add Addons Price
            addons_price = 0
            selected_addons = []
            if addon_ids:
                selected_addons = ProductAddOn.objects.filter(id__in=addon_ids)
                addons_price = sum(addon.price for addon in selected_addons)

            # Final Unit Price
            price_per_unit = base_price + addons_price
            price = price_per_unit * quantity
            total += price
            
            order_items.append({
                'product': product,
                'quantity': quantity,
                'price': price_per_unit,
                'variant': variant,
                'addons': selected_addons
            })
            
        # Add delivery fee logic
        # For simplicity, using the first product's restaurant to determine delivery fee
        # In a multi-restaurant cart, you might need more complex logic
        delivery_fee = 0
        if order_items:
            first_prod = order_items[0]['product']
            if first_prod.restaurant and validated_data.get('delivery_address') != 'Pickup':
                fee = first_prod.restaurant.get_delivery_fee(total)
                if fee is not None:
                    delivery_fee = fee
                    total += delivery_fee
            
        # Create Order
        order = Order.objects.create(
            user=user,
            total_amount=total,
            **validated_data
        )
        
        # Create Order Items
        for item in order_items:
            order_item = OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['price'],
                variant=item['variant']
            )
            if item['addons']:
                order_item.addons.set(item['addons'])

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
