"""
FILE: catalog/views.py

Filter/search/sort logic intentionally removed — that's being built by
another team member. product_list now just paginates all active products
plainly. When the filter teammate is ready, they extend THIS function
(and product_list.html) rather than replacing it.
"""

from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import Category, Product


def home(request):
    """Landing page: newest active products + all categories."""
    featured = Product.objects.filter(is_active=True).select_related('category')[:8]
    categories = Category.objects.all()

    return render(request, 'catalog/home.html', {
        'featured': featured,
        'categories': categories,
    })


def product_list(request):
    """
    All active products, plain listing, no filtering yet.
    (Search / category filter / price range / ordering to be added
    by the teammate responsible for that part.)
    """
    products = Product.objects.filter(is_active=True).select_related('category')

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'catalog/product_list.html', {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'total_count': paginator.count,
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
    """Browse active products in one category."""
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(
        category=category,
        is_active=True,
    ).select_related('category')

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'catalog/category_detail.html', {
        'category': category,
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'total_count': paginator.count,
    })


def category_list(request):
    """All categories, shown as a browsable list (nav link)."""
    categories = Category.objects.all()
    return render(request, 'catalog/category_list.html', {
        'categories': categories,
    })