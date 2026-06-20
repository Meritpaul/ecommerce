# cart/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from products.models import Product
from .cart import Cart


def _cart_summary(cart, extra=None):
    """Shared JSON summary used by all cart mutation endpoints."""
    total_price = cart.get_total_price()
    threshold   = settings.FREE_DELIVERY_THRESHOLD
    remaining   = max(0, threshold - total_price)

    data = {
        'success':                  True,
        'total_quantity':           cart.get_total_quantity(),
        'total_price':              float(total_price),
        'free_delivery_threshold':  threshold,
        'remaining_for_free':       float(remaining),
        'free_delivery_unlocked':   remaining == 0,
    }
    if extra:
        data.update(extra)
    return JsonResponse(data)


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/cart_details.html', {'cart': cart})


def cart_partial(request):
    cart = Cart(request)
    return render(request, 'cart/cart_partial.html', {'cart': cart})


def increase_item(request, id):
    cart = Cart(request)
    cart.add(id)
    return _cart_summary(cart)


def decrease_item(request, id):
    cart = Cart(request)
    cart.decrease(id)
    return _cart_summary(cart)


def remove_item(request, id):
    cart = Cart(request)
    cart.remove(id)
    return _cart_summary(cart)


def add_to_cart(request, id):
    get_object_or_404(Product, id=id)  # 404 if product doesn't exist
    cart = Cart(request)
    cart.add(id)
    return _cart_summary(cart)


def cart_api(request):
    cart = Cart(request)

    items = []
    for item in cart:
        product = item['product']
        items.append({
            'id':             product.id,
            'name':           product.name,
            'price':          float(item['unit_price']),    # discount-aware price actually charged
            'original_price': float(product.price),
            'on_sale':        product.is_on_sale,
            'quantity':       item['quantity'],
            'total':          float(item['total_price']),
            'image':          product.image.url if product.image else '',
        })

    return _cart_summary(cart, extra={'items': items})