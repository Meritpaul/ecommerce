from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from products.sitemaps import ProductSitemap, CategorySitemap, StaticSitemap

sitemaps = {
    'products':   ProductSitemap,
    'categories': CategorySitemap,
    'static':     StaticSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),

    # Apps
    path('',         include('products.urls')),
    path('cart/',    include('cart.urls')),
    path('',         include('orders.urls')),
    path('',         include('accounts.urls')),

    # SEO
    path('robots.txt', TemplateView.as_view(
        template_name='robots.txt', content_type='text/plain'
    )),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),
]

# Media files (dev only — in production nginx/CDN handles this)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
handler404 = 'products.views.error_404'
handler500 = 'products.views.error_500'