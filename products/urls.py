from django.urls import path
from . import views

urlpatterns = [
    path('',                       views.product_list,    name='product_list'),
    path('product/<int:id>/',      views.product_detail,  name='product_detail'),
    path('category/<int:id>/',     views.category_products, name='category_products'),
    path('wishlist/toggle/<int:id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/',              views.my_wishlist,     name='my_wishlist'),
]