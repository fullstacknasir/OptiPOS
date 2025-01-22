from django.contrib import admin

from purchase.models import Supplier, PurchaseOrder, PurchasedItem

# Register your models here.
admin.site.register(Supplier)
admin.site.register(PurchaseOrder)
admin.site.register(PurchasedItem)