import uuid
from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import F
from django.utils import timezone

from core.models import Store, Product
from inventory.models import Inventory, StockTransaction, MovementType


# Create your models here.
class Customer(models.Model):
    name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=100, unique=True)
    email = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name or self.name


class SalesOrderStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    COMPLETE = "COMPLETE", "Complete"
    CANCELLED = "CANCELLED", "Cancelled"


class Sales(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='sales_orders')
    store = models.ForeignKey(Store, on_delete=models.PROTECT, related_name='sales_orders')
    status = models.CharField(max_length=20, choices=SalesOrderStatus.choices, default=SalesOrderStatus.PENDING)
    sales_type = models.CharField(max_length=20, choices=(('Online', 'Online'), ('Store', 'Store')), default='Store')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                   related_name='sales_orders_created')
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"SO {self.id} ({self.get_sales_type_display()})"

    @property
    def subtotal(self):
        return sum([l.sub_total for l in self.lines.all()]) if self.lines.exists() else Decimal('0')

    @property
    def total_vat(self):
        return sum([l.vat_amount for l in self.lines.all()]) if self.lines.exists() else Decimal('0')

    @property
    def total(self):
        return self.subtotal + self.total_vat

    class Meta:
        verbose_name_plural = 'Sales'
        verbose_name = 'Sale'


class SalesLine(models.Model):
    sales = models.ForeignKey(Sales, on_delete=models.CASCADE, related_name='lines')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='sales_lines')
    inventory = models.ForeignKey(Inventory, on_delete=models.PROTECT, null=True, blank=True)
    quantity = models.DecimalField(max_digits=18, decimal_places=6, validators=[MinValueValidator(Decimal('0.000001'))])
    unit_price = models.DecimalField(max_digits=14, decimal_places=4, validators=[MinValueValidator(0)])
    sub_total = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal('0'))
    vat_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal('0'))
    discount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal('0'))
    total = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal('0'))

    def save(self, *args, **kwargs):
        self.sub_total = self.unit_price * self.quantity
        # VAT and discount logic should be improved per tax rules
        self.total = self.sub_total + (self.vat_amount or Decimal('0')) - (self.discount or Decimal('0'))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.sku} x {self.quantity}"

    class Meta:
        verbose_name_plural = 'Sales Items'
        verbose_name = 'Sales Item'


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sales = models.ForeignKey(Sales, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    method = models.CharField(max_length=30,
                              choices=(('Cash', 'Cash'), ('bKash', 'bKash'), ('Nagad', 'Nagad'), ('Card', 'Card')))
    transaction_id = models.CharField(max_length=256, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    def __str__(self):
        return self.transaction_id


class Shipment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sales_order = models.ForeignKey(Sales, on_delete=models.PROTECT, related_name="shipments")
    store = models.ForeignKey(Store, on_delete=models.PROTECT)
    shipped_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    def __str__(self):
        return f"Shipment {self.id} for SO {self.sales_order.id}"

    def ship(self, shipped_by_user):
        """
        Process the shipment by applying each ShipmentLine to inventory (atomic).
        - Creates StockTransaction entries for each line via StockTransaction.create_transaction.
        - Marks shipped_at and saves.
        - This function expects that ShipmentLines were created beforehand (one or more).
        """
        with transaction.atomic():
            # select_for_update is handled inside StockTransaction.create_transaction for Inventory row
            lines = self.lines.select_related("product", "sales_line").all()
            if not lines.exists():
                raise ValueError("Shipment has no lines to process")

            for line in lines:
                # Ensure logic to avoid double-shipping the same line (caller responsibility),
                # but the StockTransaction helper will block negative inventory.
                line.apply_to_inventory(shipped_by_user)

            # mark shipped
            self.shipped_at = timezone.now()
            self.save(update_fields=["shipped_at"])


class ShipmentLine(models.Model):
    """
    Per-product line for a Shipment. Supports partial shipments, lot/serial capture,
    and stores a price snapshot for accounting/returns.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shipment = models.ForeignKey("Shipment", on_delete=models.CASCADE, related_name="lines")
    # optional link to the originating SalesLine (for back-reference & validation)
    sales_line = models.ForeignKey("SalesLine", on_delete=models.PROTECT,
                                   null=True, blank=True, related_name="shipment_lines")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=18, decimal_places=6,
                                   validators=[MinValueValidator(Decimal('0.000001'))])
    unit_price = models.DecimalField(max_digits=14, decimal_places=4,
                                     validators=[MinValueValidator(0)], default=Decimal('0'))
    # optional: lot/serial tracking
    lot_number = models.CharField(max_length=128, blank=True, null=True)
    serial_number = models.CharField(max_length=128, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["shipment", "product"]),
            models.Index(fields=["sales_line"]),
        ]

    def __str__(self):
        return f"{self.product.sku} x {self.quantity} (Shipment {self.shipment.id})"

    def apply_to_inventory(self, shipped_by_user):
        """
        Create a negative stock transaction for this shipment line (outflow).
        Uses the central StockTransaction.create_transaction helper for safety.
        Returns the created StockTransaction.
        """
        from inventory.models import StockTransaction, MovementType

        tx = StockTransaction.create_transaction(
            product=self.product,
            store=self.shipment.store,
            quantity=-self.quantity,  # negative => reduce physical stock
            unit_cost=self.unit_price,
            movement_type=MovementType.ISSUE,
            created_by=shipped_by_user,
            reference_type='SHIP',
            reference_id=self.shipment.id,
            note=f"ShipmentLine {self.id} for SO {self.shipment.sales_order.id}"
        )

        # Optionally update shipped quantity on SalesLine if present and model has field.
        if self.sales_line is not None:
            try:
                # try using atomic DB increment if SalesLine has shipped_quantity
                if hasattr(self.sales_line, "shipped_quantity"):
                    self.sales_line.shipped_quantity = F("shipped_quantity") + self.quantity
                    self.sales_line.save(update_fields=["shipped_quantity"])
            except Exception:
                # don't raise from here — caller should handle/report
                pass

        return tx
