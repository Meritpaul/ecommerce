from django.urls import path
from .views import checkout, order_history, payment_success, payment_fail, payment_cancel

urlpatterns = [
    path('checkout/', checkout, name='checkout'),
    path('my-orders/', order_history, name='order_history'),

    # PAYMENT
    path('payment/success/', payment_success),
    path('payment/fail/', payment_fail),
    path('payment/cancel/', payment_cancel),
]