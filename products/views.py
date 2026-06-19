from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Product, Category, Banner, Wishlist

# Homepage: how many products to show per category row
HOMEPAGE_SECTION_SIZE = 8


# ─────────────────────────────────────────────
# PRODUCT LIST  (home page)
# ─────────────────────────────────────────────
def product_list(request):
    query       = request.GET.get('q', '').strip()
    category_id = request.GET.get('category')
    sort        = request.GET.get('sort', 'newest')
    page_param  = request.GET.get('page')

    products   = Product.objects.select_related('category').filter(is_active=True)
    categories = Category.objects.all()
    banners    = Banner.objects.filter(is_active=True)

    if query:
        products = products.filter(name__icontains=query)

    if category_id:
        products = products.filter(category_id=category_id)

    # Sorting
    sort_map = {
        'newest':     '-created_at',
        'oldest':     'created_at',
        'price_asc':  'price',
        'price_desc': '-price',
    }
    products = products.order_by(sort_map.get(sort, '-created_at'))

    # Pagination — 12 products per page
    paginator   = Paginator(products, 12)
    page_number = page_param or 1
    page_obj    = paginator.get_page(page_number)

    # Wishlist IDs for current user (to show filled heart)
    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = list(
            Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
        )

    # ── Homepage sections (GhorerBazar-style category rows) ──
    # Only build these when the user is browsing the plain homepage —
    # i.e. no search, no category filter, no explicit page number.
    # This keeps "filtered results" (search/category/pagination) as a
    # single clean grid, and the rich homepage layout only for the
    # default landing view.
    is_plain_homepage = not query and not category_id and not page_param
    category_sections  = []
    best_selling       = []

    if is_plain_homepage:
        best_selling = list(
            Product.objects.select_related('category')
            .filter(is_active=True, tag='best_selling')[:HOMEPAGE_SECTION_SIZE]
        )

        for cat in categories:
            cat_products = list(
                Product.objects.select_related('category')
                .filter(is_active=True, category=cat)
                .order_by('-created_at')[:HOMEPAGE_SECTION_SIZE]
            )
            if cat_products:
                category_sections.append({
                    'category': cat,
                    'products': cat_products,
                })

    return render(request, 'products/product_list.html', {
        'products':           page_obj,
        'categories':         categories,
        'banners':            banners,
        'query':              query,
        'sort':                sort,
        'sort':         sort,
        'selected_cat': category_id,
        'wishlist_ids': wishlist_ids,
    })


# ─────────────────────────────────────────────
# PRODUCT DETAIL
# ─────────────────────────────────────────────
def product_detail(request, id):
    product   = get_object_or_404(Product, id=id, is_active=True)
    related   = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=id)[:4]

    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(
            user=request.user, product=product
        ).exists()

    return render(request, 'products/product_detail.html', {
        'product':     product,
        'related':     related,
        'in_wishlist': in_wishlist,
    })


# ─────────────────────────────────────────────
# CATEGORY PRODUCTS
# ─────────────────────────────────────────────
def category_products(request, id):
    category = get_object_or_404(Category, id=id)
    products = Product.objects.filter(category=category, is_active=True).select_related('category')

    paginator   = Paginator(products, 12)
    page_obj    = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'products/product_list.html', {
        'products':     page_obj,
        'selected_cat': str(id),
        'banners':      Banner.objects.filter(is_active=True),
        'categories':   Category.objects.all(),
    })


# ─────────────────────────────────────────────
# WISHLIST TOGGLE  (AJAX)
# ─────────────────────────────────────────────
@login_required
def toggle_wishlist(request, id):
    product = get_object_or_404(Product, id=id)
    obj, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        obj.delete()
    return JsonResponse({'wishlisted': created})


# ─────────────────────────────────────────────
# MY WISHLIST PAGE
# ─────────────────────────────────────────────
@login_required
def my_wishlist(request):
    items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'products/wishlist.html', {'items': items})


# ─────────────────────────────────────────────
# ERROR PAGES
# ─────────────────────────────────────────────
def error_404(request, exception=None):
    return render(request, 'errors/404.html', status=404)

def error_500(request):
    return render(request, 'errors/500.html', status=500)


# ─────────────────────────────────────────────
# SITEMAPS
# ─────────────────────────────────────────────
class ProductSitemap(Sitemap):
    changefreq = 'daily'
    priority   = 0.9

    def items(self):
        return Product.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.created_at


class CategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority   = 0.7

    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return f'/?category={obj.id}'


class StaticSitemap(Sitemap):
    changefreq = 'monthly'
    priority   = 0.5

    def items(self):
        return ['product_list', 'login', 'register']

    def location(self, item):
        return reverse(item)