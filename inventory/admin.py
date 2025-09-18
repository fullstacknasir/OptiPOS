from django.contrib import admin

# Register your models here.
from .models import Inventory, StockTransaction

admin.site.register(Inventory)
admin.site.register(StockTransaction)