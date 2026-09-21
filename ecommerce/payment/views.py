from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import PaymentForm
from .models import Payment
from orders.models import Order, OrderItem
from cart.cart import Cart  



@login_required
def payment_success(request):
    return render(request, 'payment/success.html')


@login_required
def process_payment(request):
    cart = Cart(request)
    
    if not cart.cart: 
     return redirect('catalog:home')

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data.get('payment_method')

            order = Order.objects.create(
                user=request.user,
                shipping_full_name=f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                shipping_phone="01000000000",  
                shipping_address="Default Address",
                shipping_city="Cairo",
                total=cart.get_total_price(),
                status='confirmed'
            )

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price_at_purchase=item['price'],
                    quantity=item['quantity']
                )

            Payment.objects.create(
                user=request.user,
                amount=order.total,
                payment_method=payment_method,
                status='completed'
            )

            cart.clear()

            return redirect('payment:success')
    else:
        form = PaymentForm()

    return render(request, 'payment/checkout.html', {
        'form': form,
        'cart': cart,
        'total_price': cart.get_total_price()
    })