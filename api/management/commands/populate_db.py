
from django.core.management.base import BaseCommand
from api.models import Category, Product

class Command(BaseCommand):
    help = 'Populate database with Kenyan food data'

    def handle(self, *args, **kwargs):
        # Clear existing data
        Product.objects.all().delete()
        Category.objects.all().delete()

        categories = [
            {'name': 'Swahili Dishes', 'image': 'https://images.unsplash.com/photo-1594212699903-ec8a3eca50f5?w=500&q=80'},
            {'name': 'Nyama Choma', 'image': 'https://images.unsplash.com/photo-1544025162-d76690b67f61?w=500&q=80'},
            {'name': 'Fast Food', 'image': 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500&q=80'},
            {'name': 'Drinks', 'image': 'https://images.unsplash.com/photo-1544145945-f90425340c7e?w=500&q=80'},
        ]

        cat_objs = {}
        for cat in categories:
            obj = Category.objects.create(name=cat['name'], image=cat['image'])
            cat_objs[cat['name']] = obj
            self.stdout.write(f"Created category: {cat['name']}")

        products = [
            {
                'name': 'Pilau & Kachumbari',
                'description': 'Spiced rice cooked with beef, served with fresh tomato and onion salad.',
                'price': 450.00,
                'image': 'https://images.unsplash.com/photo-1596797038530-2c107229654b?w=500&q=80',
                'category': 'Swahili Dishes',
                'rating': 4.8,
                'calories': 650
            },
            {
                'name': 'Chapati & Beans',
                'description': 'Soft layered chapati served with coconut bean stew.',
                'price': 250.00,
                'image': 'https://thumbs.dreamstime.com/b/chapati-beans-stew-kenyan-dish-33638875.jpg',
                'category': 'Swahili Dishes',
                'rating': 4.7,
                'calories': 500
            },
            {
                'name': 'Goat Nyama Choma',
                'description': 'Grilled goat meat served with ugali and greens.',
                'price': 1200.00,
                'image': 'https://upload.wikimedia.org/wikipedia/commons/4/42/Nyama_choma_barbeque.jpg',
                'category': 'Nyama Choma',
                'rating': 4.9,
                'calories': 900
            },
            {
                'name': 'Ugali & Sukuma Wiki',
                'description': 'Classic Kenyan staple. Maize flour cake with collard greens.',
                'price': 150.00,
                'image': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=500&q=80',
                'category': 'Swahili Dishes',
                'rating': 4.5,
                'calories': 400
            },
            {
                'name': 'Matrix Burger',
                'description': 'Double beef patty, cheese, lettuce, tomato, and secret sauce.',
                'price': 850.00,
                'image': 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500&q=80',
                'category': 'Fast Food',
                'rating': 4.6,
                'calories': 850
            },
            {
                'name': 'Masala Chips',
                'description': 'French fries tossed in spicy masala sauce.',
                'price': 300.00,
                'image': 'https://images.unsplash.com/photo-1573080496987-a199f8cd75c5?w=500&q=80',
                'category': 'Fast Food',
                'rating': 4.7,
                'calories': 600
            },
            {
                'name': 'Cold Tusker',
                'description': '500ml chilled local beer.',
                'price': 350.00,
                'image': 'https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=500&q=80',
                'category': 'Drinks',
                'rating': 4.8,
                'calories': 150
            },
            {
                'name': 'Fresh Mango Juice',
                'description': 'Freshly squeezed mango juice.',
                'price': 200.00,
                'image': 'https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=500&q=80',
                'category': 'Drinks',
                'rating': 4.9,
                'calories': 120
            }
        ]

        for prod in products:
            Product.objects.create(
                name=prod['name'],
                description=prod['description'],
                price=prod['price'],
                image=prod['image'],
                category=cat_objs[prod['category']],
                rating=prod['rating'],
                calories=prod['calories']
            )
            self.stdout.write(f"Created product: {prod['name']}")

        self.stdout.write(self.style.SUCCESS('Successfully populated database'))
