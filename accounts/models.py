from django.db import models
from users.models import User

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    acc_number = models.CharField(max_length=20, unique=True)
    acc_type = models.CharField(max_length=20, default='SAVINGS')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    txn_pin = models.CharField(max_length=100, null=True, blank=True)
    opened_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.acc_number
