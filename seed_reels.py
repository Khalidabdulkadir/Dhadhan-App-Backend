import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'matrix_backend.settings')
django.setup()

from api.models import Product, Reel
import requests
from django.core.files.base import ContentFile

def download_video(url, filename):
    """Download video from URL"""
    try:
        response = requests.get(url, stream=True, timeout=30)
        if response.status_code == 200:
            return ContentFile(response.content, name=filename)
        return None
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None

def seed_reels():
    print("🎬 Starting to seed reels...")
    
    # Sample vertical food videos (9:16 ratio) - using placeholder URLs
    # In production, you'd use actual video files
    sample_videos = [
        {
            'url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
            'caption': 'Delicious burger prepared fresh! 🍔 Try our special sauce that makes it unique. Perfect for lunch or dinner!',
            'product_name': 'Burger'
        },
        {
            'url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4',
            'caption': 'Hot and cheesy pizza straight from the oven 🍕 Loaded with fresh toppings and melted mozzarella!',
            'product_name': 'Pizza'
        },
        {
            'url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4',
            'caption': 'Crispy fries seasoned to perfection 🍟 Golden and irresistible!',
            'product_name': 'Fries'
        },
    ]
    
    created_count = 0
    
    for video_data in sample_videos:
        try:
            # Find the product
            product = Product.objects.filter(name__icontains=video_data['product_name']).first()
            
            if not product:
                print(f"⚠️  Product '{video_data['product_name']}' not found, skipping...")
                continue
            
            # Check if reel already exists for this product
            existing_reel = Reel.objects.filter(product=product).first()
            if existing_reel:
                print(f"✓ Reel already exists for {product.name}")
                continue
            
            # For demo purposes, we'll create reels with URL references
            # In production, you would download actual video files
            print(f"📹 Creating reel for {product.name}...")
            
            reel = Reel.objects.create(
                product=product,
                caption=video_data['caption'],
                views=0,
                # Note: You'll need to manually upload video files to media/reels/
                # or download them using the download_video function
            )
            
            print(f"✨ Created reel for {product.name}")
            created_count += 1
            
        except Exception as e:
            print(f"❌ Error creating reel for {video_data['product_name']}: {e}")
    
    print(f"\n🎉 Successfully created {created_count} reels!")
    print(f"📝 Total reels in database: {Reel.objects.count()}")
    
    # Show all reels
    print("\n📋 Current Reels:")
    for reel in Reel.objects.all():
        print(f"  - {reel.product.name}: {reel.caption[:50]}... (Views: {reel.views})")

if __name__ == '__main__':
    seed_reels()
