from django.db import models

# Create your models here.

class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    email = models.CharField(max_length=80, unique=True)
    password = models.CharField(max_length=200)
    role = models.CharField(max_length=10, default='CUSTOMER')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
