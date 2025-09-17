from django.db import models

from core.models import Store, Product, Inventory


# Create your models here.
class Customer(models.Model):
    name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=100)
    email = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Sales(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    sales_type = models.CharField(max_length=100, choices=(('Online', 'Online'), ('Store', 'Store')), default='Store')
    sales_total = models.DecimalField(max_digits=10, decimal_places=2)
    vat_amount = models.DecimalField(max_digits=10, decimal_places=2)
    gross_total = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=100,
                              choices=(('Pending', 'Pending'), ('Complete', 'Complete'), ('Cancel', 'Cancel')),
                              default='Pending')
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.sales_type

    class Meta:
        verbose_name_plural = 'Sales'
        verbose_name = 'Sale'


class SalesItem(models.Model):
    sales = models.ForeignKey(Sales, on_delete=models.CASCADE)
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2)
    vat_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.inventory.product.name

    class Meta:
        verbose_name_plural = 'Sales Items'
        verbose_name = 'Sales Item'


class Transaction(models.Model):
    sales = models.ForeignKey(Sales, on_delete=models.CASCADE)
    transaction_amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_method = models.CharField(max_length=100, choices=(
        ('Cash', 'Cash'), ('bKash', 'bKash'), ('Nagad', 'Nagad'), ('Card', 'Card')), default='Cash')
    transaction_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.transaction_id


class Shipment(models.Model):
    sales_order = models.ForeignKey(Sales, on_delete=models.PROTECT, related_name="shipments")
    store = models.ForeignKey(Store, on_delete=models.PROTECT)
    shipped_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    def __str__(self):
        return self.sales_order.sales_type


class ShipmentLine(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=18, decimal_places=6)

    def __str__(self):
        return str(self.id)
