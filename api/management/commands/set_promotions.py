from django.core.management.base import BaseCommand
from api.models import Product

class Command(BaseCommand):
    help = 'Mark some products as promoted with discounts'

    def handle(self, *args, **kwargs):
        # Get first 3 products and mark them as promoted
        products = Product.objects.all()[:3]
        
        if not products:
            self.stdout.write(self.style.WARNING('No products found. Please add products first.'))
            return
        
        discounts = [20, 15, 25]  # Different discount percentages
        
        for i, product in enumerate(products):
            product.is_promoted = True
            product.discount_percentage = discounts[i % len(discounts)]
            product.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Promoted: {product.name} with {product.discount_percentage}% discount'
                )
            )
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Successfully promoted {len(products)} products!'))
