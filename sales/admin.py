from django.contrib import admin

from sales.models import Customer, Sales, SalesLine, Payment, Shipment, ShipmentLine

# Register your models here.
admin.site.register(Customer)
admin.site.register(Sales)
admin.site.register(SalesLine)
admin.site.register(Payment)
admin.site.register(Shipment)
admin.site.register(ShipmentLine)