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

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'discount_percentage', 'is_verified', 'is_popular', 'is_featured_campaign')
    list_editable = ('discount_percentage', 'is_verified', 'is_popular', 'is_featured_campaign')
    search_fields = ('name', 'location')

@admin.register(Reel)
class ReelAdmin(admin.ModelAdmin):
    list_display = ('product', 'is_highlight', 'views')
    list_editable = ('is_highlight',)
