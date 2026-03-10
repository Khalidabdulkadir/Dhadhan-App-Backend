from django.db import models
from django.contrib.auth.models import User

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='restaurants/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='restaurants/covers/', null=True, blank=True)
    campaign_image = models.ImageField(upload_to='restaurants/campaigns/', null=True, blank=True, help_text="Image for Hero Campaign Slider")
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Discount percentage (0-100)")
    is_verified = models.BooleanField(default=False)
    whatsapp_number = models.CharField(max_length=20)
    location = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    delivery_note = models.TextField(blank=True, help_text="Specific delivery instructions for this restaurant")
    is_popular = models.BooleanField(default=False)
    is_featured_campaign = models.BooleanField(default=False, help_text="Show as Hero Campaign on Home Screen")
    slug = models.SlugField(unique=True, blank=True)
    qr_code = models.ImageField(upload_to='restaurants/qrcodes/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            import uuid
            base_slug = slugify(self.name)
            self.slug = f"{base_slug}-{uuid.uuid4().hex[:8]}"
            
        if not self.qr_code:
            import qrcode
            from io import BytesIO
            from django.core.files import File
            
            # Use production URL structure
            qr_data = f"https://dhadhan.app/restaurants/{self.slug}"
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            file_name = f"qr_{self.slug}.png"
            
            self.qr_code.save(file_name, File(buffer), save=False)
            
        super().save(*args, **kwargs)

    # Delivery Configuration
    DELIVERY_MODE_CHOICES = (
        ('FREE', 'Free Delivery'),
        ('FIXED', 'Fixed Delivery Fee'),
        ('CONFIRM', 'Confirm via Call/WhatsApp'),
    )

    delivery_mode = models.CharField(
        max_length=20,
        choices=DELIVERY_MODE_CHOICES,
        default='CONFIRM',
        help_text="Select how delivery fee is calculated"
    )
    fixed_delivery_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Required if Delivery Mode is 'Fixed'"
    )
    free_delivery_threshold = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Order amount above which delivery is free (optional for Fixed mode)"
    )
    
    # Payment Details
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    bank_account_number = models.CharField(max_length=50, blank=True, null=True)
    paybill_number = models.CharField(max_length=20, blank=True, null=True)
    till_number = models.CharField(max_length=20, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def get_delivery_fee(self, order_total):
        """
        Calculates delivery fee based on order total.
        Returns:
            - Decimal('0.00') for Free
            - Decimal amount for Fixed
            - None for 'Confirm via Call/WhatsApp'
        """
        from decimal import Decimal
        
        # Ensure order_total is Decimal
        if not isinstance(order_total, Decimal):
            try:
                order_total = Decimal(str(order_total))
            except:
                order_total = Decimal('0.00')

        if self.delivery_mode == 'FREE':
            return Decimal('0.00')

        if self.delivery_mode == 'FIXED':
            # Check for free delivery threshold if set
            if self.free_delivery_threshold and order_total >= self.free_delivery_threshold:
                return Decimal('0.00')
            return self.fixed_delivery_fee if self.fixed_delivery_fee else Decimal('0.00')

        # Mode is CONFIRM
        return None

    def is_open_now(self):
        from django.utils import timezone
        now = timezone.localtime(timezone.now())
        current_time = now.time()
        current_day = now.weekday()
        
        try:
            oh = self.opening_hours.get(day=current_day)
            if oh.is_closed:
                return False
            
            # Normal day (e.g., 08:00 to 22:00)
            if oh.opening_time < oh.closing_time:
                return oh.opening_time <= current_time <= oh.closing_time
            # Overnight / Midnight (e.g., 18:00 to 02:00 or 06:00 to 00:00)
            else:
                return current_time >= oh.opening_time or current_time <= oh.closing_time
        except OpeningHour.DoesNotExist:
            return False

    def get_opening_status_text(self):
        from django.utils import timezone
        now = timezone.localtime(timezone.now())
        current_day = now.weekday()
        
        try:
            oh = self.opening_hours.get(day=current_day)
            if oh.is_closed:
                return "Closed for the day"
            
            curr_time = now.time()
            is_open = False
            if oh.opening_time < oh.closing_time:
                is_open = oh.opening_time <= curr_time <= oh.closing_time
            else:
                is_open = curr_time >= oh.opening_time or curr_time <= oh.closing_time

            if is_open:
                return f"Open until {oh.closing_time.strftime('%I:%M %p')}"
            elif curr_time < oh.opening_time:
                return f"Opens at {oh.opening_time.strftime('%I:%M %p')}"
            else:
                return "Closed for today"
        except OpeningHour.DoesNotExist:
            return "Hours not set"

    def __str__(self):
        return self.name

class Category(models.Model):
    restaurant = models.ForeignKey(Restaurant, related_name='categories', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    restaurant = models.ForeignKey(Restaurant, related_name='products', on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    is_hot = models.BooleanField(default=False, help_text="Show in Hot Products section")
    is_promoted = models.BooleanField(default=False)
    discount_percentage = models.IntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    calories = models.IntegerField(default=0)
    
    @property
    def effective_discount_percentage(self):
        from decimal import Decimal
        prod_discount = Decimal(self.discount_percentage) if (self.is_promoted and self.discount_percentage > 0) else Decimal(0)
        rest_discount = self.restaurant.discount_percentage if self.restaurant else Decimal(0)
        
        return max(prod_discount, rest_discount)

    @property
    def discounted_price(self):
        from decimal import Decimal
        effective_discount = self.effective_discount_percentage
        
        if effective_discount > 0:
            return self.price * (1 - (effective_discount / Decimal(100)))
        return self.price

    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)  # e.g., Small, Medium, Large
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.name} - {self.name}"

class ProductAddOn(models.Model):
    product = models.ForeignKey(Product, related_name='addons', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)  # e.g., Extra Cheese
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"+{self.name} ({self.price})"

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    addons = models.ManyToManyField(ProductAddOn, blank=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class Reel(models.Model):
    restaurant = models.ForeignKey(Restaurant, related_name='reels', on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reels')
    video = models.FileField(upload_to='reels/')
    caption = models.TextField(blank=True)
    is_highlight = models.BooleanField(default=False, help_text="Show this reel first")
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reel for {self.product.name}"

class SavedReel(models.Model):
    user = models.ForeignKey(User, related_name='saved_reels', on_delete=models.CASCADE)
    reel = models.ForeignKey(Reel, related_name='saves', on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'reel')

class FavoriteFood(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

class DirectOrder(models.Model):
    ORDER_TYPE_CHOICES = (
        ('whatsapp', 'WhatsApp'),
        ('call', 'Call'),
    )
    
    user = models.ForeignKey(User, related_name='direct_orders', on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, related_name='direct_orders', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='direct_orders', on_delete=models.SET_NULL, null=True, blank=True)
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES)
    status = models.CharField(max_length=20, default='inquiry') # Since it's external, we just track it as an inquiry
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order_type.capitalize()} Order to {self.restaurant.name} by {self.user.username}"

class OpeningHour(models.Model):
    WEEKDAYS = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    restaurant = models.ForeignKey(Restaurant, related_name="opening_hours", on_delete=models.CASCADE)
    day = models.IntegerField(choices=WEEKDAYS)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    is_closed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('restaurant', 'day')
        ordering = ('day',)

    def __str__(self):
        if self.is_closed:
            return f"{self.get_day_display()}: Closed"
        return f"{self.get_day_display()}: {self.opening_time} - {self.closing_time}"
