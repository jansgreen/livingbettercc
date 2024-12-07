from django.contrib import admin
from .models import Order

class OrderAdmin(admin.ModelAdmin):
    model = Order
    fields = ["product", "customer", "quantity", "address", "phone", "date", "status"] 

admin.site.register(Order, OrderAdmin) 
