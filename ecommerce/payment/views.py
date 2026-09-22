from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from catalog.models import Product
from orders.models import Order, OrderItem

from .forms import PaymentForm
from .models import Payment


@login_required
def payment_success(request):
    return render(
        request,
        'payment/success.html'
    )


@login_required
def process_payment(request):

    # ==========================================
    # CHECK FOR BUY NOW
    # ==========================================

    buy_now = request.session.get('buy_now')

    # ==========================================
    # BUY NOW CHECKOUT
    # ==========================================

    if buy_now:

        product_id = buy_now.get('product_id')
        quantity = buy_now.get('quantity', 1)

        product = get_object_or_404(
            Product,
            id=product_id,
            is_active=True
        )

        # Make sure quantity is valid
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            quantity = 1

        if quantity < 1:
            quantity = 1

        # Check stock
        if quantity > product.stock:

            messages.error(
                request,
                f"Only {product.stock} of "
                f"{product.name} left in stock."
            )

            return redirect(
                'catalog:product_detail',
                slug=product.slug
            )

        total_price = product.price * quantity

        checkout_items = [
            {
                'product': product,
                'quantity': quantity,
                'price': product.price,
            }
        ]

    # ==========================================
    # NORMAL CART CHECKOUT
    # ==========================================

    else:

        cart = request.session.get('cart', {})

        if not cart:

            messages.info(
                request,
                'Your cart is empty.'
            )

            return redirect('catalog:home')

        checkout_items = []
        total_price = Decimal('0.00')

        # Reconstruct Products from session
        for product_id, cart_item in cart.items():

            product = get_object_or_404(
                Product,
                id=product_id,
                is_active=True
            )

            try:
                quantity = int(
                    cart_item.get('quantity', 1)
                )
            except (TypeError, ValueError):
                quantity = 1

            if quantity < 1:
                quantity = 1

            # Stock check
            if quantity > product.stock:

                messages.error(
                    request,
                    f"Only {product.stock} of "
                    f"{product.name} left in stock."
                )

                return redirect(
                    'cart:cart_detail'
                )

            checkout_items.append(
                {
                    'product': product,
                    'quantity': quantity,
                    'price': product.price,
                }
            )

            total_price += (
                product.price * quantity
            )

    # ==========================================
    # PAYMENT FORM
    # ==========================================

    if request.method == 'POST':

        form = PaymentForm(request.POST)

        if form.is_valid():

            payment_method = (
                form.cleaned_data['payment_method']
            )

            # ==================================
            # CREATE EVERYTHING ATOMICALLY
            # ==================================

            with transaction.atomic():

                # Re-check stock immediately before
                # creating the order.
                for item in checkout_items:

                    product = item['product']

                    product.refresh_from_db()

                    if item['quantity'] > product.stock:

                        messages.error(
                            request,
                            f"Only {product.stock} of "
                            f"{product.name} left in stock."
                        )

                        return redirect(
                            'cart:cart_detail'
                        )

                # ==============================
                # USER INFORMATION
                # ==============================

                full_name = (
                    f"{request.user.first_name} "
                    f"{request.user.last_name}"
                ).strip()

                if not full_name:
                    full_name = request.user.username

                if not full_name:
                    full_name = request.user.email

                phone = getattr(
                    request.user,
                    'mobile',
                    ''
                )

                if not phone:
                    phone = "01000000000"

                # ==============================
                # CREATE ORDER
                # ==============================

                order = Order.objects.create(

                    user=request.user,

                    shipping_full_name=full_name,

                    shipping_phone=phone,

                    shipping_address="Default Address",

                    shipping_city="Cairo",

                    total=total_price,

                    status='confirmed',
                )

                # ==============================
                # CREATE ORDER ITEMS
                # ==============================

                for item in checkout_items:

                    product = item['product']

                    quantity = item['quantity']

                    OrderItem.objects.create(

                        order=order,

                        product=product,

                        price_at_purchase=(
                            item['price']
                        ),

                        quantity=quantity,
                    )

                    # Reduce stock
                    product.stock -= quantity

                    product.save(
                        update_fields=['stock']
                    )

                # ==============================
                # CREATE PAYMENT
                # ==============================

                Payment.objects.create(

                    user=request.user,

                    amount=order.total,

                    payment_method=payment_method,

                    status='completed',
                )

            # ==================================
            # CLEAR CORRECT SESSION
            # ==================================

            if buy_now:

                # Buy Now does NOT clear
                # the normal shopping cart.
                request.session.pop(
                    'buy_now',
                    None
                )

            else:

                # Normal checkout clears cart.
                request.session.pop(
                    'cart',
                    None
                )

            request.session.modified = True

            return redirect(
                'payment:success'
            )

    else:

        form = PaymentForm()

    # ==========================================
    # CHECKOUT PAGE
    # ==========================================

    return render(
        request,
        'payment/checkout.html',
        {
            'form': form,
            'checkout_items': checkout_items,
            'total_price': total_price,
            'buy_now': bool(buy_now),
        }
    )