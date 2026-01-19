
import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'matrix_backend.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import Category, Product, Order, OrderItem

def seed():
    print("Seeding data...")

    # Create Superuser if not exists
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin')
        print("Superuser 'admin' created.")

    # Create Users
    users = []
    for i in range(5):
        username = f'user{i+1}'
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username=username, email=f'{username}@example.com', password='password123', first_name=f'User{i+1}', last_name='Test')
            users.append(user)
        else:
            users.append(User.objects.get(username=username))
    print(f"Created/Found {len(users)} users.")

    # Create Categories
    categories_data = [
        {'name': 'Burgers', 'image': 'https://plus.unsplash.com/premium_photo-1683619761468-b3527e029302?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8YnVyZ2VyfGVufDB8fDB8fHww'},
        {'name': 'Pizza', 'image': 'https://images.unsplash.com/photo-1513104890138-7c749659a591?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8cGl6emF8ZW58MHx8MHx8fDA%3D'},
        {'name': 'Drinks', 'image': 'https://images.unsplash.com/photo-1437418747212-8d9709afab22?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Nnx8ZHJpbmt8ZW58MHx8MHx8fDA%3D'},
        {'name': 'Desserts', 'image': 'https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8Y2FrZXxlbnwwfHwwfHx8MA%3D%3D'},
    ]
    
    categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(name=cat_data['name'], defaults={'image': cat_data['image']})
        categories.append(category)
    print(f"Created/Found {len(categories)} categories.")

    # Create Products
    products_data = [
        {'name': 'Cheeseburger', 'price': 12.99, 'category': 'Burgers', 'image': 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8YnVyZ2VyfGVufDB8fDB8fHww'},
        {'name': 'Double Bacon Burger', 'price': 15.99, 'category': 'Burgers', 'image': 'https://images.unsplash.com/photo-1594212699903-ec8a3eca50f5?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8YnVyZ2VyfGVufDB8fDB8fHww'},
        {'name': 'Margherita Pizza', 'price': 10.99, 'category': 'Pizza', 'image': 'https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8cGl6emF8ZW58MHx8MHx8fDA%3D'},
        {'name': 'Pepperoni Pizza', 'price': 13.99, 'category': 'Pizza', 'image': 'https://images.unsplash.com/photo-1628840042765-356cda07504e?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTh8fHBpenphfGVufDB8fDB8fHww'},
        {'name': 'Cola', 'price': 2.99, 'category': 'Drinks', 'image': 'https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTN8fGNvbGF8ZW58MHx8MHx8fDA%3D'},
        {'name': 'Orange Juice', 'price': 3.99, 'category': 'Drinks', 'image': 'https://images.unsplash.com/photo-1613478223719-2ab802602423?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8b3JhbmdlJTIwanVpY2V8ZW58MHx8MHx8fDA%3D'},
        {'name': 'Chocolate Cake', 'price': 6.99, 'category': 'Desserts', 'image': 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8Y2FrZXxlbnwwfHwwfHx8MA%3D%3D'},
    ]

    products = []
    for prod_data in products_data:
        cat = Category.objects.get(name=prod_data['category'])
        prod, created = Product.objects.get_or_create(
            name=prod_data['name'], 
            defaults={
                'description': f"Delicious {prod_data['name']}",
                'price': prod_data['price'],
                'category': cat,
                'image': prod_data['image'],
                'calories': random.randint(200, 1000)
            }
        )
        products.append(prod)
    print(f"Created/Found {len(products)} products.")

    # Create Orders
    statuses = ['received', 'preparing', 'ready', 'out_for_delivery', 'delivered']
    
    # Check if we already have orders
    if not Order.objects.exists():
        for i in range(20):
            user = random.choice(users)
            status = random.choice(statuses)
            # Create order with past dates for chart
            days_ago = random.randint(0, 10)
            created_at = datetime.now() - timedelta(days=days_ago)
            
            order = Order.objects.create(
                user=user,
                status=status,
                total_amount=0, # Will calculate later
                delivery_address="123 Fake St",
            )
            order.created_at = created_at
            order.save()

            # Add items
            total_amount = 0
            num_items = random.randint(1, 4)
            for _ in range(num_items):
                product = random.choice(products)
                quantity = random.randint(1, 3)
                price = product.price * quantity
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price # Store unit price
                )
                total_amount += price
            
            order.total_amount = total_amount
            order.save()
        print("Created 20 sample orders.")
    else:
        print("Orders already exist, skipping creation.")

if __name__ == '__main__':
    seed()
