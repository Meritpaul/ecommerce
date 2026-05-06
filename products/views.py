from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from .models import Category


def product_list(request):
    query = request.GET.get('q')
    category_id = request.GET.get('category')

    products = Product.objects.all()
    categories = Category.objects.all()

    if query:
        products = products.filter(name__icontains=query)

    if category_id:
        products = products.filter(category_id=category_id)

    return render(request, 'products/product_list.html', {
        'products': products,
        'categories': categories,
        'query': query
    })


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(
        request,
        'products/product_detail.html',
        {'product': product}
    )
    

def category_products(request, id):
    category = Category.objects.get(id=id)
    products = Product.objects.filter(category=category)

    return render(request, 'products/product_list.html', {
        'products': products,
        'selected_category': category
    })