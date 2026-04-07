from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Order, OrderItem
from cart.cart import Cart
import requests


@login_required
def checkout(request):
    cart = Cart(request)

    # DELIVERY CALCULATION
    subtotal = cart.get_total_price()
    delivery = 60 if subtotal < 500 else 0
    total = subtotal + delivery

    if request.method == 'POST':

        store_id = "testbox"
        store_pass = "qwerty"

        data = {
            "store_id": store_id,
            "store_passwd": store_pass,
            "total_amount": total,
            "currency": "BDT",
            "tran_id": str(request.user.id) + "XYZ",
            "success_url": "http://127.0.0.1:8000/payment/success/",
            "fail_url": "http://127.0.0.1:8000/payment/fail/",
            "cancel_url": "http://127.0.0.1:8000/payment/cancel/",
            "cus_name": request.POST.get('name'),
            "cus_email": "test@mail.com",
            "cus_phone": request.POST.get('phone'),
            "cus_add1": request.POST.get('address'),
            "cus_city": "Dhaka",
            "cus_country": "Bangladesh",
            "shipping_method": "NO",
            "product_name": "Order",
            "product_category": "Ecommerce",
            "product_profile": "general"
        }

        response = requests.post(
            "https://sandbox.sslcommerz.com/gwprocess/v4/api.php",
            data=data
        )

        res_data = response.json()

        if res_data['status'] == 'SUCCESS':
            return redirect(res_data['GatewayPageURL'])

        return redirect('checkout')

    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'subtotal': subtotal,
        'delivery': delivery,
        'total': total
    })


# ✅ PAYMENT SUCCESS
@csrf_exempt
def payment_success(request):
    cart = Cart(request)

    order = Order.objects.create(
        user=request.user,
        total_price=cart.get_total_price(),
        name="Paid User",
        phone="N/A",
        address="Online Payment"
    )

    for item in cart:
        OrderItem.objects.create(
            order=order,
            product=item['product'],
            quantity=item['quantity'],
            price=item['product'].price
        )

    request.session['cart'] = {}

    return render(request, 'orders/checkout_success.html')


# ❌ FAIL
@csrf_exempt
def payment_fail(request):
    return render(request, 'orders/payment_fail.html')


# ⚠️ CANCEL
@csrf_exempt
def payment_cancel(request):
    return render(request, 'orders/payment_cancel.html')


# 📦 ORDER HISTORY
@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-id')

    return render(request, 'orders/order_history.html', {
        'orders': orders
    })