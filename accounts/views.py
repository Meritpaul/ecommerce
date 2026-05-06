from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
import random

# =========================
# 🔐 LOGIN (USERNAME/PASSWORD)
# =========================
def user_login(request):
    if request.method == 'POST' and 'login' in request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('product_list')
        else:
            messages.error(request, "Invalid credentials")
            return redirect('login')

    return render(request, 'accounts/login.html')


# =========================
# 📱 OTP LOGIN
# =========================
def otp_login(request):

    # SEND OTP
    if request.method == 'POST' and 'send_otp' in request.POST:
        phone = request.POST.get('phone')

        otp = str(random.randint(1000, 9999))

        request.session['otp'] = otp
        request.session['phone'] = phone

        print("OTP:", otp)  # ⚠️ check terminal

        return render(request, 'accounts/login.html', {
            'show_otp': True,
            'phone': phone
        })

    # VERIFY OTP
    if request.method == 'POST' and 'verify_otp' in request.POST:
        entered = request.POST.get('otp')
        saved = request.session.get('otp')
        phone = request.session.get('phone')

        if entered == saved:
            user, created = User.objects.get_or_create(username=phone)
            login(request, user)
            return redirect('product_list')
        else:
            messages.error(request, "Invalid OTP")
            return redirect('login')

    return redirect('login')


# =========================
# 📝 REGISTER
# =========================
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        if email and User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        user.first_name = phone  # store phone
        user.save()

        login(request, user)
        return redirect('product_list')

    return render(request, 'accounts/register.html')


# =========================
# 🚪 LOGOUT
# =========================
def user_logout(request):
    logout(request)
    return redirect('login')