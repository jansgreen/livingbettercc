from django.contrib import admin
from .models import ShippingAddress, Order, OrderItem

# Registrar ShippingAddress y OrderItem
admin.site.register(ShippingAddress)
admin.site.register(OrderItem)

# Inline para OrderItem
class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0

# Personalización del admin de Order
class OrderAdmin(admin.ModelAdmin):
    model = Order
    readonly_fields = ["date_ordered"]
    fields = ["user", "full_name", "email", "shipping_address", "amount_paid", "date_ordered", "shipped", "date_shipped"]
    inlines = [OrderItemInline]

# Registrar el modelo Order con su configuración personalizada
admin.site.register(Order, OrderAdmin)
