from django.urls import path
from . import views

urlpatterns = [
    path('checkout/',          views.checkout,        name='checkout'),
    path('my-orders/',         views.order_history,   name='order_history'),
    path('payment/success/',   views.payment_success, name='payment_success'),
    path('payment/fail/',      views.payment_fail,    name='payment_fail'),
    path('payment/cancel/',    views.payment_cancel,  name='payment_cancel'),
]