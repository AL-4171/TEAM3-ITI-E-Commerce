from django.shortcuts import get_object_or_404, redirect, render
from catalog.models import Product

def cart_detail(request):
  cart = request.session.get('cart', {})
  return render(request, 'cart/cart_detail.html', {'cart': cart})

def add_to_cart(request, product_id):
  product = get_object_or_404(Product, id=product_id)
  cart = request.session.get('cart', {})

  if str(product_id) in cart:
    cart[str(product_id)]['quantity'] += 1
  else:
    cart[str(product_id)] = {
        'name': product.name,
        'price': str(product.price),
        'quantity': 1,
    }

  request.session['cart'] = cart
  request.session.modified = True
  return redirect('cart:cart_detail')

def increment_quantity(request, product_id):
  cart = request.session.get('cart', {})
  if str(product_id) in cart:
    cart[str(product_id)]['quantity'] += 1
    request.session['cart'] = cart
  return redirect('cart:cart_detail')

def decrement_quantity(request, product_id):
  cart = request.session.get('cart', {})
  if str(product_id) in cart:
    if cart[str(product_id)]['quantity'] > 1:
      cart[str(product_id)]['quantity'] -= 1
    else:
      del cart[str(product_id)]
    request.session['cart'] = cart
  return redirect('cart:cart_detail')

def remove_from_cart(request, product_id):
  cart = request.session.get('cart', {})
  if str(product_id) in cart:
    del cart[str(product_id)]
    request.session['cart'] = cart
  return redirect('cart:cart_detail')

def clear_cart(request):
  if 'cart' in request.session:
    del request.session['cart']
    return redirect('cart:cart_detail')