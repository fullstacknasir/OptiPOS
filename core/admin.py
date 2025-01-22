from django.contrib import admin

from core.models import Store, Category, Brand, Inventory, Product, Adjustment, Transfer

# Register your models here.
admin.site.register(Store)
admin.site.register(Brand)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Adjustment)
admin.site.register(Inventory)
admin.site.register(Transfer)