from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import PaymentForm
from .models import Payment

@login_required
def process_payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data.get('payment_method')
            
            # Save transaction to database
            Payment.objects.create(
                user=request.user,
                amount=100.00,
                payment_method=payment_method,
                status='completed'
            )
            # Redirect directly to success page
            return redirect('payment:success')
    else:
        form = PaymentForm()

    return render(request, 'payment/checkout.html', {'form': form})

def payment_success(request):
    return render(request, 'payment/success.html')








