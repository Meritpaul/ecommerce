# cart/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('partial/', views.cart_partial, name='cart_partial'),
    path('increase/<int:id>/', views.increase_item, name='increase_item'),
    path('decrease/<int:id>/', views.decrease_item, name='decrease_item'),
    path('remove/<int:id>/', views.remove_item, name='remove_item'),
    path('api/', views.cart_api, name='cart_api'),
]