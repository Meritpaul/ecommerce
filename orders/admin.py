from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model  = OrderItem
    extra  = 0
    readonly_fields = ('product', 'quantity', 'price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display   = ('id', 'user', 'name', 'phone', 'total_price', 'status', 'created_at')
    list_filter    = ('status', 'created_at')
    list_editable  = ('status',)
    search_fields  = ('name', 'phone', 'transaction_id', 'user__username')
    readonly_fields = ('transaction_id', 'created_at', 'updated_at')
    inlines        = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')