from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.contrib.auth import logout
from django.db import IntegrityError
from .models import User
from accounts.models import Account
import random

def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')

        try:
            user = User.objects.get(username=u)
            if check_password(p, user.password):
                request.session['uid'] = user.id
                messages.success(request, "Login successful")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid credentials")
        except User.DoesNotExist:
            messages.error(request, "User not found")

    return render(request, 'login.html')


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "This username is already taken. Please choose another.")
            return render(request, 'register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered. Please use another.")
            return render(request, 'register.html')

        try:
            user = User(
                username=username,
                email=email,
                password=make_password(password)
            )
            user.save()

            acc = Account(
                user=user,
                acc_number=generate_acc(),
                balance=0.00
            )
            acc.save()

            messages.success(request, "Account created successfully!")
            return redirect('login')

        except IntegrityError:
            messages.error(request, "Something went wrong while creating your account. Please try again.")

    return render(request, 'register.html')


def dashboard(request):
    uid = request.session.get('uid')
    if not uid:
        return redirect('login')

    user = User.objects.get(id=uid)
    account = Account.objects.get(user=user)

    masked = "XXXX" + account.acc_number[-2:]

    return render(request, 'dashboard.html', {
        'user': user,
        'acc': account,
        'masked': masked
    })


def logout_view(request):
    logout(request)
    request.session.flush()
    storage = messages.get_messages(request)
    for _ in storage:
        pass
    messages.success(request, "Logout successful")
    return redirect('login')


def support(request):
    return render(request, 'support.html')


def about(request):
    return render(request, 'about.html')

def generate_acc():
    return "MH" + str(random.randint(100000, 999999))