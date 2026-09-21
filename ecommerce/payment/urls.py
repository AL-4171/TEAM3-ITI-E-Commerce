from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('checkout/', views.process_payment, name='checkout'),
    path('success/', views.payment_success, name='success'),
]

