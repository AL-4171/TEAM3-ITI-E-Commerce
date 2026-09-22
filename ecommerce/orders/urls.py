from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.order_history, name='order_history'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('manage/', views.admin_order_list, name='admin_order_list'),
    path('manage/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
]