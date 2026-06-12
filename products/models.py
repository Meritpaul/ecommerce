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
    category    = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        related_name='products', null=True, blank=True
    )
    name        = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    image       = models.ImageField(upload_to='products/')
    stock       = models.IntegerField(default=0)
    created_at  = models.DateTimeField(default=timezone.now)
    is_active   = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.id])

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