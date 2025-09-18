from django.contrib import admin

from purchase.models import Supplier, PurchaseOrder, PurchaseOrderLine, PurchaseReceipt

# Register your models here.
admin.site.register(Supplier)
admin.site.register(PurchaseOrder)
admin.site.register(PurchaseOrderLine)
admin.site.register(PurchaseReceipt)
