from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    extra = 0
    fields = ('phone', 'address')


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'phone_number', 'is_staff', 'date_joined')

    def phone_number(self, obj):
        try:
            return obj.profile.phone or '—'
        except UserProfile.DoesNotExist:
            return '—'
    phone_number.short_description = 'Phone'


# Re-register User with the customized admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)