from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import Order


@login_required
def order_history(request):
	orders = Order.objects.filter(user=request.user)
	return render(request, 'orders/order_history.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
	order = get_object_or_404(
		Order.objects.prefetch_related('items__product'),
		id=order_id,
		user=request.user,
	)
	return render(request, 'orders/order_detail.html', {'order': order})


@staff_member_required
def admin_order_list(request):
	orders = Order.objects.select_related('user').all()
	return render(request, 'orders/admin_order_list.html', {'orders': orders})
