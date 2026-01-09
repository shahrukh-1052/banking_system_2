from django.db import models
from accounts.models import Account

class Transaction(models.Model):
    from_acc = models.ForeignKey(
        Account, related_name='from_transactions',
        on_delete=models.CASCADE, null=True)

    to_acc = models.ForeignKey(
        Account, related_name='to_transactions',
        on_delete=models.CASCADE, null=True)

    txn_type = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, default='SUCCESS')
    message = models.CharField(max_length=120)
    done_at = models.DateTimeField(auto_now_add=True)
