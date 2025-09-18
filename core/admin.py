from django.contrib import admin

from core.models import Store, StoreUser, Category, Brand, Product

admin.site.register(Store)
admin.site.register(StoreUser)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Product)