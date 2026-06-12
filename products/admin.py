from django.contrib import admin
from .models import Product, Category, Banner, Wishlist


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ('name',)
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display   = ('name', 'category', 'price', 'stock', 'is_active', 'created_at')
    list_filter    = ('category', 'is_active')
    list_editable  = ('price', 'stock', 'is_active')
    search_fields  = ('name', 'description')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {'fields': ('name', 'category', 'description', 'image')}),
        ('Pricing & Stock', {'fields': ('price', 'stock', 'is_active')}),
        ('Timestamps', {'fields': ('created_at',)}),
    )


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display  = ('title', 'order', 'is_active')
    list_editable = ('order', 'is_active')


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    list_filter  = ('user',)