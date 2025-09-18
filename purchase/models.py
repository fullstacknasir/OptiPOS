import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.utils import timezone

from core.models import Product, Store
from inventory.models import StockTransaction, MovementType


# Create your models here.
class Supplier(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class PurchaseOrderStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    ORDERED = "ORDERED", "Ordered"
    RECEIVED = "RECEIVED", "Received"
    CANCELLED = "CANCELLED", "Cancelled"


class PurchaseOrder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchase_orders')
    store = models.ForeignKey(Store, on_delete=models.PROTECT, related_name='purchase_orders')
    status = models.CharField(max_length=20, choices=PurchaseOrderStatus.choices, default=PurchaseOrderStatus.PENDING)
    order_date = models.DateField(default=timezone.now)
    expected_delivery_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    class Meta:
        indexes = [models.Index(fields=["supplier", "store", "status"])]

    def __str__(self):
        return f"PO {self.id} - {self.supplier.name}"

    @property
    def subtotal(self):
        return sum([line.line_total for line in self.lines.all()]) if self.lines.exists() else Decimal('0')

    @property
    def total_vat(self):
        return sum([line.vat for line in self.lines.all()]) if self.lines.exists() else Decimal('0')

    @property
    def total(self):
        return self.subtotal + self.total_vat


class PurchaseOrderLine(models.Model):
    purchase = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='lines')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='purchase_lines')
    quantity = models.DecimalField(max_digits=18, decimal_places=6, validators=[MinValueValidator(Decimal('0.000001'))])
    unit_price = models.DecimalField(max_digits=14, decimal_places=4, validators=[MinValueValidator(0)])
    vat = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal('0'))
    line_total = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal('0'))

    def save(self, *args, **kwargs):
        self.line_total = (self.unit_price * self.quantity) + (self.vat or Decimal('0'))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.sku} x {self.quantity}"


class PurchaseReceipt(models.Model):
    """
    When goods are physically received, create a receipt referencing PO and create stock transactions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT, related_name='receipts')
    store = models.ForeignKey(Store, on_delete=models.PROTECT)
    received_at = models.DateTimeField(auto_now_add=True)
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                    related_name='purchase_receipts')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Receipt {self.id} for PO {self.purchase.id}"

    def apply_to_inventory(self):
        """
        Create StockTransaction entries for each purchased line (atomic).
        """
        with transaction.atomic():
            lines = self.purchase.lines.select_related('product').all()
            for line in lines:
                # increase stock by the purchased quantity
                StockTransaction.create_transaction(
                    product=line.product,
                    store=self.store,
                    quantity=line.quantity,
                    unit_cost=line.unit_price,
                    movement_type=MovementType.RECEIPT,
                    created_by=self.received_by,
                    reference_type='PO',
                    reference_id=self.purchase.id,
                    note=f"Receipt for PO {self.purchase.id}"
                )
