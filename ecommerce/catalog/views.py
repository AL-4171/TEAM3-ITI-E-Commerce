"""
FILE: catalog/views.py

Filter/search/sort logic intentionally removed — that's being built by
another team member. product_list now just paginates all active products
plainly. When the filter teammate is ready, they extend THIS function
(and product_list.html) rather than replacing it.
"""

from django.core.paginator import Paginator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CategoryForm, ProductForm
from .models import Category, Product


def home(request):
    """Landing page: newest active products + category count/tiles."""
    active_products = Product.objects.filter(is_active=True)
    featured = active_products.select_related('category')[:4]
    categories = Category.objects.all()

    return render(request, 'catalog/home.html', {
        'featured': featured,
        'categories': categories,
        'total_count': active_products.count(),
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

    return render(request, 'catalog/category_products.html', {
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


# ============================================================
# ADMIN — CATEGORY MANAGEMENT (staff only)
# ============================================================
@staff_member_required
def admin_dashboard(request):
    """Staff landing page for all available store-management sections."""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    context = {
        'category_count': Category.objects.count(),
        'product_count': Product.objects.count(),
        'user_count': User.objects.count(),
    }

    try:
        from orders.models import Order
    except (ImportError, ModuleNotFoundError):
        context['order_count'] = None
    else:
        context['order_count'] = Order.objects.count()

    return render(request, 'catalog/admin/admin_dashboard.html', context)
@staff_member_required
def admin_dashboard(request):
    """Staff landing page for all available store-management sections."""
    context = {
        'category_count': Category.objects.count(),
        'product_count': Product.objects.count(),
    }

    try:
        from orders.models import Order
    except (ImportError, ModuleNotFoundError):
        context['order_count'] = None
    else:
        context['order_count'] = Order.objects.count()

    return render(request, 'catalog/admin/admin_dashboard.html', context)

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


# ============================================================
# ADMIN — PRODUCT MANAGEMENT (staff only)
# ============================================================

@staff_member_required
def admin_product_list(request):
    products = Product.objects.select_related('category').all()
    return render(request, 'catalog/admin/product_manage_list.html', {'products': products})


@staff_member_required
def admin_product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product created.')
            return redirect('catalog:admin_product_list')
    else:
        form = ProductForm()
    return render(request, 'catalog/admin/product_form.html', {
        'form': form, 'page_title': 'Add Product', 'submit_label': 'Create Product',
    })


@staff_member_required
def admin_product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated.')
            return redirect('catalog:admin_product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'catalog/admin/product_form.html', {
        'form': form, 'page_title': f'Edit {product.name}', 'submit_label': 'Save Changes',
    })


@staff_member_required
def admin_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted.')
        return redirect('catalog:admin_product_list')
    return render(request, 'catalog/admin/product_confirm_delete.html', {'product': product})



# ============================================================
# ADMIN — USER MANAGEMENT (staff only, toggle-only, no deletion)
# ============================================================

@staff_member_required
def admin_user_list(request):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'catalog/admin/user_manage_list.html', {'users': users})


@staff_member_required
def admin_user_toggle_staff(request, pk):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        if user_obj == request.user:
            messages.error(request, "You can't change your own admin status.")
        else:
            user_obj.is_staff = not user_obj.is_staff
            user_obj.save()
            messages.success(request, f"{user_obj.email} is now {'an admin' if user_obj.is_staff else 'a customer'}.")
    return redirect('catalog:admin_user_list')


@staff_member_required
def admin_user_toggle_active(request, pk):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        if user_obj == request.user:
            messages.error(request, "You can't deactivate your own account.")
        else:
            user_obj.is_active = not user_obj.is_active
            user_obj.save()
            messages.success(request, f"{user_obj.email} is now {'active' if user_obj.is_active else 'deactivated'}.")
    return redirect('catalog:admin_user_list')