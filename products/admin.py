from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Product, Category, Banner, Wishlist


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ('thumbnail', 'name', 'product_count')
    search_fields = ('name',)

    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:40px;height:40px;object-fit:cover;border-radius:8px;" />',
                obj.image.url
            )
        return mark_safe('<span style="font-size:24px;">🌿</span>')
    thumbnail.short_description = ''

    def product_count(self, obj):
        count = obj.products.count()
        return format_html('<b>{}</b> products', count)
    product_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display   = ('thumbnail', 'name', 'category', 'price', 'stock_badge', 'is_active', 'created_at')
    list_filter    = ('category', 'is_active')
    list_editable  = ('price', 'is_active')
    search_fields  = ('name', 'description')
    readonly_fields = ('created_at', 'image_preview')
    list_per_page  = 25

    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'category', 'description')
        }),
        ('Image', {
            'fields': ('image', 'image_preview')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:48px;height:48px;object-fit:cover;border-radius:8px;" />',
                obj.image.url
            )
        return '—'
    thumbnail.short_description = ''

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:300px;max-height:300px;border-radius:12px;" />',
                obj.image.url
            )
        return 'No image uploaded yet'
    image_preview.short_description = 'Preview'

    def stock_badge(self, obj):
        if obj.stock == 0:
            color, text = '#ef4444', 'Out of Stock'
        elif obj.stock <= 5:
            color, text = '#f97316', f'Low — {obj.stock} left'
        else:
            color, text = '#22c55e', f'{obj.stock} in stock'
        return format_html(
            '<span style="background:{}1a;color:{};padding:3px 10px;border-radius:999px;'
            'font-size:12px;font-weight:600;">{}</span>',
            color, color, text
        )
    stock_badge.short_description = 'Stock'


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display  = ('thumbnail', 'title', 'order', 'is_active')
    list_editable = ('order', 'is_active')

    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:80px;height:40px;object-fit:cover;border-radius:6px;" />',
                obj.image.url
            )
        return '—'
    thumbnail.short_description = 'Preview'


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    list_filter  = ('user',)