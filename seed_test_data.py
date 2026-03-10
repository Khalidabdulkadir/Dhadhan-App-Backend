
import os
import django
import random
import requests
from io import BytesIO
from django.core.files import File
from datetime import time

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'matrix_backend.settings')
django.setup()

from api.models import Restaurant, Category, Product, ProductVariant, ProductAddOn, OpeningHour

def download_image(url, filename):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return File(BytesIO(response.content), name=filename)
    except Exception as e:
        print(f"⚠️ Failed to download image from {url}: {e}")
    return None

def seed_data():
    print("🗑️ Deleting all existing data...")
    Restaurant.objects.all().delete()
    
    print("🏗️ Creating sample restaurants with images...")
    
    # 1. Burger Palace
    burger_palace = Restaurant.objects.create(
        name="Burger Palace",
        description="The best burgers in town with fresh ingredients.",
        location="Downtown Avenue 42",
        whatsapp_number="+254712345678",
        is_verified=True,
        is_popular=True,
        is_featured_campaign=True,
        delivery_mode='FIXED',
        fixed_delivery_fee=150.00,
        free_delivery_threshold=2000.00
    )

    # Images for Burger Palace
    logo = download_image("https://images.unsplash.com/photo-1594212699903-ec8a3eca50f5?q=80&w=200&h=200&auto=format&fit=crop", "burger_logo.jpg")
    if logo: burger_palace.logo.save("burger_logo.jpg", logo, save=False)
    
    cover = download_image("https://images.unsplash.com/photo-1550547660-d9450f859349?q=80&w=800&h=400&auto=format&fit=crop", "burger_cover.jpg")
    if cover: burger_palace.cover_image.save("burger_cover.jpg", cover, save=False)

    campaign = download_image("https://images.unsplash.com/photo-1571091718767-18b5b1457add?q=80&w=800&h=400&auto=format&fit=crop", "burger_campaign.jpg")
    if campaign: burger_palace.campaign_image.save("burger_campaign.jpg", campaign, save=False)
    
    burger_palace.save()

    # Opening Hours
    for day in range(7):
        OpeningHour.objects.create(
            restaurant=burger_palace,
            day=day,
            opening_time=time(8, 0),
            closing_time=time(22, 0),
            is_closed=False
        )

    # 2. Sushi Zen
    sushi_zen = Restaurant.objects.create(
        name="Sushi Zen",
        description="Authentic Japanese sushi and ramen experience.",
        location="Ocean View Drive",
        whatsapp_number="+254788888888",
        is_verified=True,
        is_featured_campaign=True,
        delivery_mode='FREE'
    )

    logo_s = download_image("https://images.unsplash.com/photo-1579871494447-9811cf80d66c?q=80&w=200&h=200&auto=format&fit=crop", "sushi_logo.jpg")
    if logo_s: sushi_zen.logo.save("sushi_logo.jpg", logo_s, save=False)
    
    cover_s = download_image("https://images.unsplash.com/photo-1553621042-f6e147245754?q=80&w=800&h=400&auto=format&fit=crop", "sushi_cover.jpg")
    if cover_s: sushi_zen.cover_image.save("sushi_cover.jpg", cover_s, save=False)
    
    # Add a dedicated campaign image for Sushi Zen
    camp_s = download_image("https://images.unsplash.com/photo-1579584425555-c3ce17fd4111?q=80&w=800&h=400&auto=format&fit=crop", "sushi_campaign.jpg")
    if camp_s: sushi_zen.campaign_image.save("sushi_campaign.jpg", camp_s, save=False)
    
    sushi_zen.save()

    # 3. Pizza Planet
    pizza_planet = Restaurant.objects.create(
        name="Pizza Planet",
        description="Wood-fired pizzas with premium toppings.",
        location="Upper Hill",
        whatsapp_number="+254700000000",
        is_verified=True,
        is_featured_campaign=True,
        delivery_mode='FIXED',
        fixed_delivery_fee=100.0
    )

    logo_p = download_image("https://images.unsplash.com/photo-1513104890138-7c749659a591?q=80&w=200&h=200&auto=format&fit=crop", "pizza_logo.jpg")
    if logo_p: pizza_planet.logo.save("pizza_logo.jpg", logo_p, save=False)
    
    camp_p = download_image("https://images.unsplash.com/photo-1593560708920-61dd98c46a4e?q=80&w=800&h=400&auto=format&fit=crop", "pizza_campaign.jpg")
    if camp_p: pizza_planet.campaign_image.save("pizza_campaign.jpg", camp_p, save=False)
    
    pizza_planet.save()

    # Opening Hours for remaining
    for r in [sushi_zen, pizza_planet]:
        for day in range(6):
            OpeningHour.objects.create(restaurant=r, day=day, opening_time=time(11, 0), closing_time=time(21, 0))
        OpeningHour.objects.create(restaurant=r, day=6, opening_time=time(0, 0), closing_time=time(0, 0), is_closed=True)

    # Categories
    burger_cat = Category.objects.create(restaurant=burger_palace, name="Burgers")
    cat_img_b = download_image("https://images.unsplash.com/photo-1550547660-d9450f859349?q=80&w=200&h=200&auto=format&fit=crop", "cat_burger.jpg")
    if cat_img_b: burger_cat.image.save("cat_burger.jpg", cat_img_b)

    sides_cat = Category.objects.create(restaurant=burger_palace, name="Sides")
    cat_img_s = download_image("https://images.unsplash.com/photo-1573080491719-202e7422237e?q=80&w=200&h=200&auto=format&fit=crop", "cat_sides.jpg")
    if cat_img_s: sides_cat.image.save("cat_sides.jpg", cat_img_s)

    # Products
    classic_burger = Product.objects.create(
        restaurant=burger_palace,
        category=burger_cat,
        name="Classic Beef Burger",
        description="Juicy beef patty with lettuce, tomato, and our secret sauce.",
        price=850.00,
        is_hot=True,
        calories=650
    )
    prod_img_b = download_image("https://images.unsplash.com/photo-1568901346375-23c9450c58cd?q=80&w=400&h=300&auto=format&fit=crop", "classic_burger.jpg")
    if prod_img_b: classic_burger.image.save("classic_burger.jpg", prod_img_b)

    ProductVariant.objects.create(product=classic_burger, name="Single Patty", price=850.00, is_default=True)
    ProductVariant.objects.create(product=classic_burger, name="Double Patty", price=1100.00)
    ProductAddOn.objects.create(product=classic_burger, name="Extra Cheese", price=100.00)

    fries = Product.objects.create(
        restaurant=burger_palace,
        category=sides_cat,
        name="Golden Fries",
        description="Crispy salted potato fries.",
        price=250.00
    )
    prod_img_f = download_image("https://images.unsplash.com/photo-1573080491719-202e7422237e?q=80&w=400&h=300&auto=format&fit=crop", "fries.jpg")
    if prod_img_f: fries.image.save("fries.jpg", prod_img_f)

    print("✅ Seed data with images created successfully!")

if __name__ == "__main__":
    seed_data()
