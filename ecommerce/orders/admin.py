from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
	model = OrderItem
	extra = 0
	fields = ('product', 'quantity', 'price_at_purchase')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'created_at', 'total', 'status')
	list_filter = ('status', 'created_at')
	search_fields = ('user__email',)
	inlines = (OrderItemInline,)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
	list_display = ('order', 'product', 'quantity', 'price_at_purchase')
	list_select_related = ('order', 'product')
