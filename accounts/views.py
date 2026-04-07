from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # ✅ check passwords match
        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect('register')

        # ✅ check username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        # ✅ create user
        user = User.objects.create_user(username=username, password=password1)

        # ✅ auto login after register
        login(request, user)

        return redirect('product_list')

    return render(request, 'accounts/register.html')