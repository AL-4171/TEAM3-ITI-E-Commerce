from django.shortcuts import render, redirect, get_object_or_404
from catalog.models import Product

def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    
    for product_id, item in cart.items():
        subtotal = float(item['price']) * int(item['quantity'])
        total += subtotal
        cart_items.append({
            'product_id': product_id,
            'name': item['name'],
            'price': item['price'],
            'quantity': item['quantity'],
            'subtotal': subtotal,
        })
        
    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'cart/cart_detail.html', context)

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    
    if str(product_id) in cart:
        if cart[str(product_id)]['quantity'] < product.stock:
            cart[str(product_id)]['quantity'] += 1
    else:
        if product.stock > 0:
            cart[str(product_id)] = {
                'name': product.name,
                'price': str(product.price),
                'quantity': 1,
            }
            
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
