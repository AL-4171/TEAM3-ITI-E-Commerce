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

from .forms import CategoryForm, ProductForm , UserManageForm
from .models import Category, Product
from django.contrib.auth import get_user_model
from orders.models import Order

User = get_user_model()



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

    return render(request, 'catalog/category_products.html', {
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


# ============================================================
# ADMIN — CATEGORY MANAGEMENT (staff only)
# ============================================================

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

# =========================================================
# ADMIN DASHBOARD
# =========================================================

@staff_member_required
def admin_dashboard(request):
    return render(
        request,
        "catalog/admin/admin_dashboard.html",
        {
            "order_count": Order.objects.count(),
            "category_count": Category.objects.count(),
            "product_count": Product.objects.count(),
            "user_count": User.objects.count(),
        },
    )

# =========================================================
# ADMIN — USER MANAGEMENT
# =========================================================

@staff_member_required
def admin_user_list(request):
    users = User.objects.all().order_by("-date_joined")

    return render(
        request,
        "catalog/admin/user_manage_list.html",
        {
            "users": users,
        },
    )


@staff_member_required
def admin_user_add(request):
    if request.method == "POST":
        form = UserManageForm(
            request.POST,
            request_user=request.user,
        )

        if form.is_valid():
            user = form.save()

            messages.success(
                request,
                f"User {user.get_username()} was created successfully."
            )

            return redirect("catalog:admin_user_list")
    else:
        form = UserManageForm(
            request_user=request.user,
        )

    return render(
        request,
        "catalog/admin/user_manage_form.html",
        {
            "form": form,
            "page_title": "Add User",
            "submit_label": "Create User",
        },
    )


@staff_member_required
def admin_user_edit(request, pk):
    managed_user = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        form = UserManageForm(
            request.POST,
            instance=managed_user,
            request_user=request.user,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "User updated successfully."
            )

            return redirect("catalog:admin_user_list")
    else:
        form = UserManageForm(
            instance=managed_user,
            request_user=request.user,
        )

    return render(
        request,
        "catalog/admin/user_manage_form.html",
        {
            "form": form,
            "managed_user": managed_user,
            "page_title": "Edit User",
            "submit_label": "Save Changes",
        },
    )


@staff_member_required
def admin_user_delete(request, pk):
    managed_user = get_object_or_404(User, pk=pk)

    # Prevent an admin from deleting their own account
    if managed_user == request.user:
        messages.error(
            request,
            "You cannot delete your own account."
        )
        return redirect("catalog:admin_user_list")

    if request.method == "POST":
        username = managed_user.get_username()
        managed_user.delete()

        messages.success(
            request,
            f"User {username} was deleted successfully."
        )

        return redirect("catalog:admin_user_list")

    return render(
        request,
        "catalog/admin/user_confirm_delete.html",
        {
            "managed_user": managed_user,
        },
    )


@staff_member_required
def admin_user_toggle_staff(request, pk):
    managed_user = get_object_or_404(User, pk=pk)

    if managed_user == request.user:
        messages.error(
            request,
            "You cannot change your own staff status."
        )
        return redirect("catalog:admin_user_list")

    managed_user.is_staff = not managed_user.is_staff
    managed_user.save(update_fields=["is_staff"])

    messages.success(
        request,
        "Staff status updated successfully."
    )

    return redirect("catalog:admin_user_list")


@staff_member_required
def admin_user_toggle_active(request, pk):
    managed_user = get_object_or_404(User, pk=pk)

    if managed_user == request.user:
        messages.error(
            request,
            "You cannot deactivate your own account."
        )
        return redirect("catalog:admin_user_list")

    managed_user.is_active = not managed_user.is_active
    managed_user.save(update_fields=["is_active"])

    messages.success(
        request,
        "Account status updated successfully."
    )

    return redirect("catalog:admin_user_list")
