from django.contrib import admin

from sales.models import Customer, Sales, SalesItem, Transaction

# Register your models here.
admin.site.register(Customer)
admin.site.register(Sales)
admin.site.register(SalesItem)
admin.site.register(Transaction)