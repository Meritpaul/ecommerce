import secrets
import logging
from datetime import timedelta

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.utils import timezone

from .models import UserProfile
from .utils import normalize_bd_phone

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# LOGIN (username / password)
# ─────────────────────────────────────────────
def user_login(request):
    if request.user.is_authenticated:
        return redirect('product_list')

    if request.method == 'POST' and 'login' in request.POST:
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')


# ─────────────────────────────────────────────
# OTP LOGIN (phone number)
# ─────────────────────────────────────────────
def otp_login(request):
    # Step 1 — send OTP
    if request.method == 'POST' and 'send_otp' in request.POST:
        raw_phone = request.POST.get('phone', '').strip()
        phone = normalize_bd_phone(raw_phone)

        if not phone:
            messages.error(request, 'Please enter a valid Bangladeshi phone number (e.g. 01812345678 or +8801812345678).')
            return redirect('login')

        otp    = str(secrets.randbelow(900000) + 100000)   # 6-digit secure OTP
        expiry = (timezone.now() + timedelta(minutes=5)).isoformat()

        request.session['otp']        = otp
        request.session['otp_expiry'] = expiry
        request.session['otp_phone']  = phone

        # ── Send real SMS here ───────────────────────────────────────
        # from your_sms_module import send_sms
        # send_sms(phone, f"Your PureShop OTP: {otp}. Valid for 5 minutes.")
        # ────────────────────────────────────────────────────────────

        # Dev only — remove in production
        logger.info('DEV OTP for %s: %s', phone, otp)

        messages.success(request, f'OTP sent to {phone}. (Check terminal in dev mode)')
        return render(request, 'accounts/login.html', {
            'show_otp': True,
            'phone': phone,
        })

    # Step 2 — verify OTP
    if request.method == 'POST' and 'verify_otp' in request.POST:
        entered = request.POST.get('otp', '').strip()
        saved   = request.session.get('otp')
        expiry  = request.session.get('otp_expiry')
        phone   = request.session.get('otp_phone')

        if not (saved and expiry and phone):
            messages.error(request, 'Session expired. Please try again.')
            return redirect('login')

        if timezone.now().isoformat() > expiry:
            messages.error(request, 'OTP expired. Please request a new one.')
            return redirect('login')

        if entered != saved:
            messages.error(request, 'Invalid OTP. Please try again.')
            return render(request, 'accounts/login.html', {
                'show_otp': True,
                'phone': phone,
            })

        # OTP valid — log in (or create) user
        user, created = User.objects.get_or_create(username=phone)
        if created:
            user.set_unusable_password()
            user.save()
            UserProfile.objects.get_or_create(user=user, defaults={'phone': phone})

        login(request, user)

        # Clean up session
        for key in ('otp', 'otp_expiry', 'otp_phone'):
            request.session.pop(key, None)

        return redirect('product_list')

    return redirect('login')


# ─────────────────────────────────────────────
# REGISTER
# ─────────────────────────────────────────────
def register(request):
    if request.user.is_authenticated:
        return redirect('product_list')

    if request.method == 'POST':
        username   = request.POST.get('username', '').strip()
        email      = request.POST.get('email', '').strip()
        raw_phone  = request.POST.get('phone', '').strip()
        phone      = normalize_bd_phone(raw_phone)
        password1  = request.POST.get('password1', '')
        password2  = request.POST.get('password2', '')

        # Validation
        errors = []
        if not phone:
            errors.append('Please enter a valid Bangladeshi phone number (e.g. 01812345678 or +8801812345678).')
        if password1 != password2:
            errors.append('Passwords do not match.')
        if len(password1) < 8:
            errors.append('Password must be at least 8 characters.')
        if User.objects.filter(username=username).exists():
            errors.append('Username already taken.')
        if email and User.objects.filter(email=email).exists():
            errors.append('An account with this email already exists.')

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, 'accounts/register.html', {
                'form_data': {'username': username, 'email': email, 'phone': raw_phone}
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
        )
        # Save normalized phone in UserProfile (NOT in first_name)
        UserProfile.objects.filter(user=user).update(phone=phone)

        login(request, user)
        messages.success(request, f'Welcome to PureShop, {username}! 🎉')
        return redirect('product_list')

    return render(request, 'accounts/register.html')


# ─────────────────────────────────────────────
# LOGOUT
# ─────────────────────────────────────────────
def user_logout(request):
    logout(request)
    return redirect('login')