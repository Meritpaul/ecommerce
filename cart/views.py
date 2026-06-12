# cart/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from products.models import Product
from .cart import Cart


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/cart_details.html', {'cart': cart})


def cart_partial(request):
    cart = Cart(request)
    return render(request, 'cart/cart_partial.html', {'cart': cart})


def increase_item(request, id):
    cart = Cart(request)
    cart.add(id)
    return JsonResponse({
        'success': True,
        'total_quantity': cart.get_total_quantity(),
        'total_price': float(cart.get_total_price()),
    })


def decrease_item(request, id):
    cart = Cart(request)
    cart.decrease(id)
    return JsonResponse({
        'success': True,
        'total_quantity': cart.get_total_quantity(),
        'total_price': float(cart.get_total_price()),
    })


def remove_item(request, id):
    cart = Cart(request)
    cart.remove(id)
    return JsonResponse({
        'success': True,
        'total_quantity': cart.get_total_quantity(),
        'total_price': float(cart.get_total_price()),
    })


def add_to_cart(request, id):
    get_object_or_404(Product, id=id)  # 404 if product doesn't exist
    cart = Cart(request)
    cart.add(id)
    return JsonResponse({
        'success': True,
        'total_quantity': cart.get_total_quantity(),
        'total_price': float(cart.get_total_price()),
    })


def cart_api(request):
    cart = Cart(request)

    items = []
    for item in cart:
        items.append({
            'id':       item['product'].id,
            'name':     item['product'].name,
            'price':    float(item['product'].price),
            'quantity': item['quantity'],
            'total':    float(item['total_price']),
            'image':    item['product'].image.url if item['product'].image else '',
        })

    return JsonResponse({
        'items':          items,
        'total_price':    float(cart.get_total_price()),
        'total_quantity': cart.get_total_quantity(),
    })