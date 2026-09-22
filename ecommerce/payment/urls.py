from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('checkout/', views.process_payment, name='checkout'),
    path(
        'buy-now/<int:product_id>/',
        views.process_payment,
        name='buy_now'
    ),
    path('success/', views.payment_success, name='success'),
]

