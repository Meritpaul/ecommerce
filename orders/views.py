import logging
import requests as http_requests

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib import messages

from .models import Order, OrderItem
from cart.cart import Cart

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# CHECKOUT
# ─────────────────────────────────────────────
@login_required
def checkout(request):
    cart = Cart(request)

    if len(cart) == 0:
        messages.warning(request, 'Your cart is empty.')
        return redirect('product_list')

    subtotal = cart.get_total_price()
    threshold = settings.FREE_DELIVERY_THRESHOLD
    delivery = settings.DELIVERY_CHARGE if subtotal < threshold else 0
    total    = subtotal + delivery
    remaining_for_free = max(0, threshold - subtotal)

    if request.method == 'POST':
        name    = request.POST.get('name', '').strip()
        phone   = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()

        if not (name and phone and address):
            messages.error(request, 'Please fill in all fields.')
            return render(request, 'orders/checkout.html', {
                'cart': cart, 'subtotal': subtotal,
                'delivery': delivery, 'total': total,
                'remaining_for_free': remaining_for_free,
            })

        # Save shipping info in session for payment_success to use
        request.session['pending_order'] = {
            'name': name, 'phone': phone,
            'address': address, 'total': float(total),
        }

        # Generate unique transaction ID
        import uuid
        tran_id = f'PS-{request.user.id}-{uuid.uuid4().hex[:8].upper()}'

        data = {
            'store_id':         settings.SSLCOMMERZ_STORE_ID,
            'store_passwd':     settings.SSLCOMMERZ_STORE_PASS,
            'total_amount':     float(total),
            'currency':         'BDT',
            'tran_id':          tran_id,
            'success_url':      f'{settings.SITE_URL}/payment/success/?tran_id={tran_id}',
            'fail_url':         f'{settings.SITE_URL}/payment/fail/',
            'cancel_url':       f'{settings.SITE_URL}/payment/cancel/',
            'cus_name':         name,
            'cus_email':        request.user.email or 'customer@pureshop.com',
            'cus_phone':        phone,
            'cus_add1':         address,
            'cus_city':         'Dhaka',
            'cus_country':      'Bangladesh',
            'shipping_method':  'NO',
            'product_name':     'PureShop Order',
            'product_category': 'Ecommerce',
            'product_profile':  'general',
        }

        try:
            response  = http_requests.post(settings.SSLCOMMERZ_API_URL, data=data, timeout=30)
            res_data  = response.json()

            if res_data.get('status') == 'SUCCESS':
                return redirect(res_data['GatewayPageURL'])
            else:
                logger.error('SSLCommerz error: %s', res_data)
                messages.error(request, 'Payment gateway error. Please try again.')
        except Exception as e:
            logger.error('SSLCommerz request failed: %s', e)
            messages.error(request, 'Could not connect to payment gateway. Please try again.')

    return render(request, 'orders/checkout.html', {
        'cart':     cart,
        'subtotal': subtotal,
        'delivery': delivery,
        'total':    total,
        'remaining_for_free': remaining_for_free,
    })


# ─────────────────────────────────────────────
# PAYMENT SUCCESS
# ─────────────────────────────────────────────
@csrf_exempt
def payment_success(request):
    if not request.user.is_authenticated:
        return redirect('login')

    tran_id      = request.GET.get('tran_id') or request.POST.get('tran_id', '')
    pending      = request.session.get('pending_order')

    if not pending:
        messages.warning(request, 'Order data not found. Please contact support.')
        return redirect('order_history')

    # Prevent duplicate order for same transaction
    if tran_id and Order.objects.filter(transaction_id=tran_id).exists():
        return redirect('order_history')

    cart = Cart(request)

    order = Order.objects.create(
        user           = request.user,
        name           = pending.get('name', ''),
        phone          = pending.get('phone', ''),
        address        = pending.get('address', ''),
        total_price    = pending.get('total', cart.get_total_price()),
        transaction_id = tran_id or None,
        status         = 'paid',
    )

    for item in cart:
        product  = item['product']
        quantity = item['quantity']

        OrderItem.objects.create(
            order    = order,
            product  = product,
            quantity = quantity,
            price    = product.price,
        )

        # Reduce stock (don't go below 0)
        product.stock = max(0, product.stock - quantity)
        product.save(update_fields=['stock'])

    cart.clear()
    request.session.pop('pending_order', None)

    return render(request, 'orders/checkout_success.html', {'order': order})


# ─────────────────────────────────────────────
# PAYMENT FAIL / CANCEL
# ─────────────────────────────────────────────
@csrf_exempt
def payment_fail(request):
    return render(request, 'orders/payment_fail.html')


@csrf_exempt
def payment_cancel(request):
    return render(request, 'orders/payment_cancel.html')


# ─────────────────────────────────────────────
# ORDER HISTORY
# ─────────────────────────────────────────────
@login_required
def order_history(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .prefetch_related('items__product')
        .order_by('-created_at')
    )
    return render(request, 'orders/order_history.html', {'orders': orders})