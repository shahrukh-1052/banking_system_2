from django.urls import path
from . import views

urlpatterns = [
    path('deposit/', views.deposit, name='deposit'),
    path('withdraw/', views.withdraw, name='withdraw'),
    path('transfer/', views.transfer, name='transfer'),

    # call correct name → history
    path('history/', views.history, name='history'),
]
