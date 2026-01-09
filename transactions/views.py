from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.models import Account
from .models import Transaction
from django.db import transaction
from decimal import Decimal, InvalidOperation
from django.contrib.auth.hashers import check_password
from users.models import User



def deposit(request):
    uid = request.session.get('uid')
    acc = Account.objects.get(user_id=uid)

    if request.method == 'POST':
        raw_amount = request.POST.get('amount', '').strip()
        if not raw_amount:
            messages.error(request, "Please enter an amount")
            return render(request, 'deposit.html')

        try:
            amt = Decimal(raw_amount)
        except InvalidOperation:
            messages.error(request, "Invalid amount entered")
            return render(request, 'deposit.html')

        if amt <= 0:
            messages.error(request, "Amount must be greater than zero")
            return render(request, 'deposit.html')

        acc.balance += amt
        acc.save()

        Transaction(
            to_acc=acc,
            txn_type='DEPOSIT',
            amount=amt,
            message='Deposit Done'
        ).save()

        messages.success(request, f"Deposited {amt} successfully")
        return render(request, 'deposit.html')

    return render(request, 'deposit.html')




def withdraw(request):
    uid = request.session.get('uid')
    acc = Account.objects.get(user_id=uid)

    if request.method == 'POST':
        raw_amount = request.POST.get('amount', '').strip()
        if not raw_amount:
            messages.error(request, "Please enter an amount")
            return render(request, 'withdraw.html')

        try:
            amt = Decimal(raw_amount)
        except InvalidOperation:
            messages.error(request, "Invalid amount entered")
            return render(request, 'withdraw.html')

        if amt <= 0:
            messages.error(request, "Amount must be greater than zero")
            return render(request, 'withdraw.html')

        if acc.balance < amt:
            messages.error(request, "Insufficient Funds")
            return render(request, 'withdraw.html')

        acc.balance -= amt
        acc.save()

        Transaction(
            from_acc=acc,
            txn_type='WITHDRAW',
            amount=amt,
            message='Withdraw Done'
        ).save()

        messages.success(request, f"Withdrawn {amt} successfully")
        return render(request, 'withdraw.html')

    return render(request, 'withdraw.html')

def history(request):
    uid = request.session.get('uid')
    if not uid:
        return redirect('login')

    acc = Account.objects.get(user_id=uid)

    # Fetch all transactions where this account is sender or receiver
    txns = (Transaction.objects.filter(from_acc=acc) | Transaction.objects.filter(to_acc=acc)).order_by('-done_at')

    return render(request, 'history.html', {'txns': txns})




def transfer(request):
    uid = request.session.get('uid')
    sender = Account.objects.get(user_id=uid)
    user = User.objects.get(id=uid)

    if request.method == 'POST':
        to_acc_num = request.POST.get('to', '').strip()
        raw_amount = request.POST.get('amount', '').strip()
        note = request.POST.get('message', '').strip()
        password = request.POST.get('password', '').strip()  # only present in step 2

        # Step 1: Validate receiver + amount + balance BEFORE asking password
        if not password:  # means user hasn't entered password yet
            if not to_acc_num or not raw_amount:
                messages.error(request, "Receiver account and amount are required")
                return render(request, 'transfer.html')

            try:
                amt = Decimal(raw_amount)
            except InvalidOperation:
                messages.error(request, "Invalid amount entered")
                return render(request, 'transfer.html')

            if amt <= 0:
                messages.error(request, "Amount must be greater than zero")
                return render(request, 'transfer.html')

            try:
                receiver = Account.objects.get(acc_number=to_acc_num)
            except Account.DoesNotExist:
                messages.error(request, "Receiver account not found")
                return render(request, 'transfer.html')

            if sender.balance < amt:
                messages.error(request, "Insufficient Funds")
                return render(request, 'transfer.html')

            return render(request, 'transfer.html', {
                'show_password_popup': True,
                'to_acc_num': to_acc_num,
                'amount': raw_amount,
                'message': note
            })

        # Step 2: Validate password and perform transfer
        if not check_password(password, user.password):
            messages.error(request, "Invalid account password")
            return render(request, 'transfer.html')

        amt = Decimal(raw_amount)
        receiver = Account.objects.get(acc_number=to_acc_num)

        with transaction.atomic():
            sender.balance -= amt
            receiver.balance += amt
            sender.save()
            receiver.save()

            Transaction(
                from_acc=sender,
                to_acc=receiver,
                txn_type='TRANSFER',
                amount=amt,
                message=note or 'Transfer Done'
            ).save()

        messages.success(request, f"Transferred {amt} to {receiver.acc_number} successfully")
        return render(request, 'transfer.html')

    return render(request, 'transfer.html')
