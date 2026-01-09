from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from .models import User
from accounts.models import Account
from django.contrib.auth import logout
import random

def generate_acc():
    return "MH" + str(random.randint(100000, 999999))


def login_view(request):
    if request.method == 'POST':
        u = request.POST['username']
        p = request.POST['password']

        print("TRY LOGIN USER:", u)   # debug

        try:
            user = User.objects.get(username=u)

            print("USER FROM DB:", user.username)

            if check_password(p, user.password):

                request.session['uid'] = user.id

                messages.success(request,
                    "Login Successful")

                return redirect('dashboard')
            else:
                messages.error(request,
                    "Invalid Credentials")

        except Exception as e:
            print("LOGIN ERROR:", e)
            messages.error(request,
                "User Not Found")

    return render(request, 'login.html')




def register_view(request):
    if request.method == 'POST':

        username = request.POST['username']
        email = request.POST['email']
        password = make_password(request.POST['password'])

        user = User(username=username, email=email,
                    password=password)
        user.save()

        # create account automatically
        acc = Account(user=user,
                      acc_number=generate_acc(),
                      balance=0.00)
        acc.save()

        messages.success(request,
            "Account Created Successfully")

        return redirect('login')

    return render(request, 'register.html')



def dashboard(request):
    uid = request.session.get('uid')

    if not uid:
        return redirect('login')

    user = User.objects.get(id=uid)
    account = Account.objects.get(user=user)

    # psychological security → masking
    masked = "XXXX" + account.acc_number[-2:]

    return render(request, 'dashboard.html',
        {'user': user,
         'acc': account,
         'masked': masked})



def logout_view(request):
    logout(request)
    request.session.flush()   # clear session
    storage = messages.get_messages(request)
    for _ in storage:  # iterate to clear leftover messages
        pass
    messages.success(request, "Logout successful")
    return redirect('login')


def support(request):
    return render(request, 'support.html')

def about(request):
    return render(request, 'about.html')