from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

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


@staff_member_required
def admin_order_detail(request, order_id):
	"""Staff view of a single order, with the ability to update its status."""
	order = get_object_or_404(
		Order.objects.select_related('user').prefetch_related('items__product'),
		id=order_id,
	)

	if request.method == 'POST':
		new_status = request.POST.get('status')
		valid_statuses = dict(Order.STATUS_CHOICES)
		if new_status in valid_statuses:
			order.status = new_status
			order.save(update_fields=['status'])
			messages.success(request, f"Order #{order.id} marked as {valid_statuses[new_status]}.")
			return redirect('orders:admin_order_detail', order_id=order.id)

	return render(request, 'orders/admin_order_detail.html', {'order': order})