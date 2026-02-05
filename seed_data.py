
import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'matrix_backend.settings')
django.setup()

from api.models import Restaurant, Category, Product, ProductVariant, ProductAddOn

def seed_variants():
    print("Seeding variants and delivery data...")

    # 1. Setup 'Pizza Palace' (Fixed Delivery Fee)
    restaurant1, _ = Restaurant.objects.get_or_create(
        name="Pizza Palace",
        defaults={
            'whatsapp_number': '254712345678',
            'location': 'Eastleigh, First Ave',
            'is_verified': True,
            'is_popular': True
        }
    )
    # Update pricing model
    restaurant1.delivery_mode = 'FIXED'
    restaurant1.fixed_delivery_fee = Decimal('200.00')
    restaurant1.free_delivery_threshold = Decimal('2000.00')
    restaurant1.save()

    # Category
    cat_pizza, _ = Category.objects.get_or_create(
        name="Pizzas", 
        restaurant=restaurant1,
        defaults={'image': None}
    )

    # Product: Chicken Periperi Pizza
    pizza_prod, created = Product.objects.get_or_create(
        name="Chicken Periperi Pizza",
        restaurant=restaurant1,
        defaults={
            'description': "Spicy chicken pizza with periperi sauce",
            'price': Decimal('1000.00'), # Base price (fallback)
            'category': cat_pizza,
            'image': 'products/pizza_sample.jpg', # Assuming generic path
            'rating': 4.5
        }
    )

    # Add Variants logic
    # Clear existing to avoid duplicates in this test
    # pizza_prod.variants.all().delete()
    # pizza_prod.addons.all().delete()

    if not pizza_prod.variants.exists():
        ProductVariant.objects.create(product=pizza_prod, name="Small", price=Decimal('800.00'))
        ProductVariant.objects.create(product=pizza_prod, name="Medium", price=Decimal('1000.00'), is_default=True)
        ProductVariant.objects.create(product=pizza_prod, name="Large", price=Decimal('1400.00'))
        print(f"Added variants to {pizza_prod.name}")

    if not pizza_prod.addons.exists():
        ProductAddOn.objects.create(product=pizza_prod, name="Extra Cheese", price=Decimal('150.00'))
        ProductAddOn.objects.create(product=pizza_prod, name="Extra Mushrooms", price=Decimal('100.00'))
        ProductAddOn.objects.create(product=pizza_prod, name="Extra Chicken", price=Decimal('200.00'))
        print(f"Added addons to {pizza_prod.name}")


    # 2. Setup 'Burger Joint' (Free Delivery)
    restaurant2, _ = Restaurant.objects.get_or_create(
        name="Burger Joint",
        defaults={
            'whatsapp_number': '254787654321',
            'location': 'Town Center',
            'is_verified': True
        }
    )
    restaurant2.delivery_mode = 'FREE'
    restaurant2.fixed_delivery_fee = None
    restaurant2.free_delivery_threshold = None
    restaurant2.save()

    cat_burger, _ = Category.objects.get_or_create(
        name="Burgers",
        restaurant=restaurant2
    )

    burger_prod, _ = Product.objects.get_or_create(
        name="Classic Beef Burger",
        restaurant=restaurant2,
        defaults={
            'description': "Juicy beef patty with cheese and lettuce",
            'price': Decimal('600.00'),
            'category': cat_burger,
            'rating': 4.8
        }
    )

    if not burger_prod.variants.exists():
        ProductVariant.objects.create(product=burger_prod, name="Single", price=Decimal('600.00'), is_default=True)
        ProductVariant.objects.create(product=burger_prod, name="Double Value", price=Decimal('900.00'))

    if not burger_prod.addons.exists():
        ProductAddOn.objects.create(product=burger_prod, name="Extra Bacon", price=Decimal('150.00'))
        ProductAddOn.objects.create(product=burger_prod, name="Extra Cheese", price=Decimal('50.00'))


    # 3. Setup 'Local Swahili' (Confirm via Message)
    restaurant3, _ = Restaurant.objects.get_or_create(
        name="Swahili Dishes",
        defaults={
            'whatsapp_number': '254700000000',
            'location': 'Majengo'
        }
    )
    restaurant3.delivery_mode = 'CONFIRM' 
    restaurant3.save()

    cat_swahili, _ = Category.objects.get_or_create(
        name="Lunch",
        restaurant=restaurant3
    )

    pilau_prod, _ = Product.objects.get_or_create(
        name="Pilau Beef",
        restaurant=restaurant3,
        defaults={
            'description': "Traditional pilau with beef stew",
            'price': Decimal('400.00'),
            'category': cat_swahili
        }
    )
    # No variants for this one, just to test simple products

    print("Seeding complete!")

if __name__ == '__main__':
    seed_variants()
