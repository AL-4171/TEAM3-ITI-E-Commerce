from django.urls import path

from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('categories/', views.category_list, name='category_list'),
    path('category/<slug:slug>/', views.category_products, name='category_detail'),
    path("category/<slug:slug>/", views.category_products, name="category_products"),
    # --- custom admin dashboard ---
    path('catalog/manage/', views.admin_dashboard, name='admin_dashboard'),
    # --- admin: category management ---
    path('catalog/manage/categories/', views.admin_category_list, name='admin_category_list'),
    path('catalog/manage/categories/add/', views.admin_category_add, name='admin_category_add'),
    path('catalog/manage/categories/<int:pk>/edit/', views.admin_category_edit, name='admin_category_edit'),
    path('catalog/manage/categories/<int:pk>/delete/', views.admin_category_delete, name='admin_category_delete'),

    # --- admin: product management ---
    path('catalog/manage/products/', views.admin_product_list, name='admin_product_list'),
    path('catalog/manage/products/add/', views.admin_product_add, name='admin_product_add'),
    path('catalog/manage/products/<int:pk>/edit/', views.admin_product_edit, name='admin_product_edit'),
    path('catalog/manage/products/<int:pk>/delete/', views.admin_product_delete, name='admin_product_delete'),

    # --- admin: user management (toggle-only, no deletion) ---
    path('catalog/manage/users/', views.admin_user_list, name='admin_user_list'),
    path('catalog/manage/users/<int:pk>/toggle-staff/', views.admin_user_toggle_staff, name='admin_user_toggle_staff'),
    path('catalog/manage/users/<int:pk>/toggle-active/', views.admin_user_toggle_active, name='admin_user_toggle_active'),
]