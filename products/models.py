from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from PIL import Image as PILImage
import os


class Category(models.Model):
    name  = models.CharField(max_length=100)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/?category={self.id}'


class Product(models.Model):
    TAG_CHOICES = [
        ('',             '— No Tag —'),
        ('best_selling', 'Best Selling'),
        ('new_arrival',  'New Arrival'),
        ('pre_order',    'Pre Order'),
    ]

    category       = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        related_name='products', null=True, blank=True
    )
    name           = models.CharField(max_length=200)
    description    = models.TextField(blank=True)
    price          = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text='Original price. If a discount price is also set, this will show as a crossed-out price.'
    )
    discount_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True,
        help_text='Optional sale price. Must be lower than the original price. Leave empty for no discount.'
    )
    tag            = models.CharField(
        max_length=20, choices=TAG_CHOICES, blank=True, default='',
        help_text='Optional badge shown on the product card (e.g. "Best Selling").'
    )
    image          = models.ImageField(upload_to='products/')
    stock          = models.IntegerField(default=0)
    created_at     = models.DateTimeField(default=timezone.now)
    is_active      = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.id])

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.discount_price is not None and self.discount_price >= self.price:
            raise ValidationError({
                'discount_price': 'Discount price must be lower than the original price.'
            })

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Auto-resize large images to save storage & speed up pages
        if self.image:
            try:
                img_path = self.image.path
                img = PILImage.open(img_path)
                max_size = (800, 800)
                if img.width > max_size[0] or img.height > max_size[1]:
                    img.thumbnail(max_size, PILImage.LANCZOS)
                    # Convert RGBA → RGB so we can save as JPEG
                    if img.mode in ('RGBA', 'P'):
                        img = img.convert('RGB')
                    img.save(img_path, optimize=True, quality=85)
            except Exception:
                pass  # Don't crash if image processing fails

    @property
    def is_on_sale(self):
        return self.discount_price is not None and self.discount_price < self.price

    @property
    def display_price(self):
        """The price the customer actually pays."""
        return self.discount_price if self.is_on_sale else self.price

    @property
    def discount_percent(self):
        """Whole-number percentage saved, e.g. 8 for 'Save 8%'. 0 if not on sale."""
        if not self.is_on_sale or self.price == 0:
            return 0
        saved = self.price - self.discount_price
        return int(round((saved / self.price) * 100))

    @property
    def amount_saved(self):
        """TK amount saved, e.g. 200 for 'Save ৳200'. 0 if not on sale."""
        if not self.is_on_sale:
            return 0
        return self.price - self.discount_price

    @property
    def tag_label(self):
        return dict(self.TAG_CHOICES).get(self.tag, '')


class Banner(models.Model):
    image     = models.ImageField(upload_to='banners/')
    title     = models.CharField(max_length=200, blank=True)
    link      = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    order     = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title or f'Banner {self.id}'


class Wishlist(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlists')
    product    = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f'{self.user.username} → {self.product.name}'