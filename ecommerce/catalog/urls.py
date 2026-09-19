from django.urls import path
 
from . import views
 
app_name = 'catalog'
 
urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/<slug:slug>/', views.category_products, name='category_detail'),
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    path('catalog/manage/categories/', views.admin_category_list, name='admin_category_list'),
    path('catalog/manage/categories/add/', views.admin_category_add, name='admin_category_add'),
    path(
        'catalog/manage/categories/<int:pk>/edit/',
        views.admin_category_edit,
        name='admin_category_edit',
    ),
    path(
        'catalog/manage/categories/<int:pk>/delete/',
        views.admin_category_delete,
        name='admin_category_delete',
    ),
]
 