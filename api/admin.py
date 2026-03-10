from django.contrib import admin
from .models import *
# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'discount_percentage', 'is_promoted', 'restaurant')
    list_filter = ('restaurant', 'category', 'is_promoted')
    search_fields = ('name', 'description')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')

class OpeningHourInline(admin.TabularInline):
    model = OpeningHour
    extra = 7

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'discount_percentage', 'is_verified', 'is_popular', 'is_featured_campaign', 'slug')
    list_editable = ('discount_percentage', 'is_verified', 'is_popular', 'is_featured_campaign')
    readonly_fields = ('slug', 'qr_code')
    search_fields = ('name', 'location')
    inlines = [OpeningHourInline]

@admin.register(Reel)
class ReelAdmin(admin.ModelAdmin):
    list_display = ('product', 'is_highlight', 'views')
    list_editable = ('is_highlight',)

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'price', 'is_default')
    list_filter = ('product', 'is_default')

@admin.register(ProductAddOn)
class ProductAddOnAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'price', 'is_available')
    list_filter = ('product', 'is_available')
@admin.register(OpeningHour)
class OpeningHourAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'day', 'opening_time', 'closing_time', 'is_closed')
    list_filter = ('day', 'is_closed')
    search_fields = ('restaurant__name',)
