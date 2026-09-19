"""
FILE: catalog/views.py

Integrated full search, category filtering, price range, and ordering 
logic into product_list & category_products while maintaining pagination.
"""

from django.core.paginator import Paginator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CategoryForm
from .models import Category, Product


def home(request):
    """Landing page: newest active products."""
    featured = Product.objects.filter(is_active=True).select_related('category')[:8]

    return render(request, 'catalog/home.html', {
        'featured': featured,
    })


def product_list(request):
    """
    All active products with Search, Category Filter, Price Range, 
    and Ordering, with pagination support.
    """
    products = Product.objects.filter(is_active=True).select_related('category')
    categories = Category.objects.all()

    search_query = request.GET.get('q', '').strip()
    if search_query:
        products = products.filter(name__icontains=search_query)

    category_id = request.GET.get('category', '').strip()
    if category_id:
        products = products.filter(category_id=category_id)

    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()

    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    sort_by = request.GET.get('sort', '').strip()
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'name_asc':
        products = products.order_by('name')
    elif sort_by == 'name_desc':
        products = products.order_by('-name')

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'catalog/product_list.html', {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'total_count': paginator.count,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
    })


def product_detail(request, slug):
    """Single product page — shows every field from the spec (18-24)."""
    product = get_object_or_404(
        Product.objects.select_related('category'),
        slug=slug,
        is_active=True,
    )

    related = Product.objects.filter(
        category=product.category,
        is_active=True,
    ).exclude(pk=product.pk)[:4]

    return render(request, 'catalog/product_detail.html', {
        'product': product,
        'related': related,
    })


def category_products(request, slug):
    """Browse active products in one category with filter, search, and sort."""
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(
        category=category,
        is_active=True,
    ).select_related('category')

    search_query = request.GET.get('q', '').strip()
    if search_query:
        products = products.filter(name__icontains=search_query)

    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()

    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    sort_by = request.GET.get('sort', '').strip()
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'name_asc':
        products = products.order_by('name')
    elif sort_by == 'name_desc':
        products = products.order_by('-name')

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'catalog/category_detail.html', {
        'category': category,
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'total_count': paginator.count,
        'search_query': search_query,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
    })


def category_list(request):
    """All categories, shown as a browsable list (nav link)."""
    categories = Category.objects.all()
    return render(request, 'catalog/category_list.html', {
        'categories': categories,
    })


@staff_member_required
def admin_category_list(request):
    """Manage categories from the storefront for staff users."""
    categories = Category.objects.annotate(product_count=Count('products'))
    return render(request, 'catalog/admin/category_manage_list.html', {
        'categories': categories,
    })


@staff_member_required
def admin_category_add(request):
    """Create a category from the storefront."""
    form = CategoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Category created successfully.')
        return redirect('catalog:admin_category_list')

    return render(request, 'catalog/admin/category_form.html', {
        'form': form,
        'page_title': 'Add Category',
        'submit_label': 'Create Category',
    })


@staff_member_required
def admin_category_edit(request, pk):
    """Edit an existing category from the storefront."""
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Category updated successfully.')
        return redirect('catalog:admin_category_list')

    return render(request, 'catalog/admin/category_form.html', {
        'form': form,
        'category': category,
        'page_title': 'Edit Category',
        'submit_label': 'Save Changes',
    })


@staff_member_required
def admin_category_delete(request, pk):
    """Confirm and delete a category unless products still reference it."""
    category = get_object_or_404(Category, pk=pk)
    error_message = None

    if request.method == 'POST':
        try:
            category.delete()
        except ProtectedError:
            error_message = (
                'This category cannot be deleted because it has products '
                'attached to it.'
            )
        else:
            messages.success(request, 'Category deleted successfully.')
            return redirect('catalog:admin_category_list')

    return render(request, 'catalog/admin/category_confirm_delete.html', {
        'category': category,
        'error_message': error_message,
    })