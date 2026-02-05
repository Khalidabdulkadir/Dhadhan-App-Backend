
import os
import django
from django.utils.text import slugify
import uuid

# Setup Django environment
import sys
sys.path.append('..') # Add the parent directory to Python path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'matrix_backend.settings')
django.setup()

from api.models import Restaurant
import qrcode
from io import BytesIO
from django.core.files import File

def populate_slugs_and_qrs():
    restaurants = Restaurant.objects.all()
    count = 0
    for restaurant in restaurants:
        updated = False
        if not restaurant.slug:
            base_slug = slugify(restaurant.name)
            restaurant.slug = f"{base_slug}-{uuid.uuid4().hex[:8]}"
            updated = True
            
        if not restaurant.qr_code:
            # Use production URL structure
            qr_data = f"https://dhadhan.app/restaurants/{restaurant.slug}"
            
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
            file_name = f"qr_{restaurant.slug}.png"
            
            restaurant.qr_code.save(file_name, File(buffer), save=False)
            updated = True

        if updated:
            restaurant.save()
            count += 1
            print(f"Updated {restaurant.name} with slug: {restaurant.slug}")

    print(f"Successfully updated {count} restaurants.")

if __name__ == '__main__':
    populate_slugs_and_qrs()
