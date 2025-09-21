import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import Q
from django.core.exceptions import ValidationError

from core.models import Product, Store


# Create your models here.
class MovementType(models.TextChoices):
    RECEIPT = "RECEIPT", "Receipt"
    ISSUE = "ISSUE", "Issue"
    TRANSFER_IN = "TRANSFER_IN", "Transfer In"
    TRANSFER_OUT = "TRANSFER_OUT", "Transfer Out"
    ADJUST = "ADJUST", "Adjust"
    COUNT = "COUNT", "Stocktake"


class Inventory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='inventories')
    store = models.ForeignKey(Store, on_delete=models.PROTECT, related_name='inventories')
    quantity = models.DecimalField(max_digits=18, decimal_places=6, default=0,
                                   validators=[MinValueValidator(Decimal('0'))])
    stock_alert = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    discount_method = models.CharField(max_length=100, choices=(('percentage', 'percentage'), ('flat', 'flat')))
    discount_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Inventory"
        verbose_name_plural = "Inventory"
        constraints = [
            models.CheckConstraint(check=Q(quantity__gte=0), name="inventory_qty_nonnegative"),
            models.CheckConstraint(check=Q(stock_alert__gte=0), name="inventory_stock_alert_nonnegative"),
            models.CheckConstraint(check=Q(discount_rate__gte=0), name="inventory_discount_rate_nonnegative"),
            # percentage → 0..100, flat → >=0
            models.CheckConstraint(
                name="inventory_discount_rate_bounds",
                check=(
                        Q(discount_method='percentage', discount_rate__gte=0, discount_rate__lte=100)
                        | Q(discount_method='flat', discount_rate__gte=0)
                ),
            ),
            models.UniqueConstraint(fields=["product", "store"], name="uniq_inventory_product_store"),
        ]
        indexes = [
            models.Index(fields=["product", "store"]),
            models.Index(fields=["updated_at"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.product.name

    def adjust_quantity(self, delta, created_by, movement_type=MovementType.ADJUST, ref_type=None, ref_id=None,
                        note=""):
        """
        Safely adjust quantity via ledger. This is the recommended path (atomic).
        Returns created StockTransaction instance.
        """
        return StockTransaction.create_transaction(
            product=self.product,
            store=self.store,
            quantity=delta,
            unit_cost=self.product.unit_cost,
            movement_type=movement_type,
            created_by=created_by,
            reference_type=ref_type,
            reference_id=ref_id,
            note=note,
        )


class StockTransaction(models.Model):
    """
    Immutable ledger of stock movements. Every inventory change must create one.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='stock_transactions')
    store = models.ForeignKey(Store, on_delete=models.PROTECT, related_name='stock_transactions')
    quantity = models.DecimalField(max_digits=18, decimal_places=6)  # positive for IN, negative for OUT convention
    unit_cost = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    movement_type = models.CharField(max_length=24, choices=MovementType.choices)
    reference_type = models.CharField(max_length=32, null=True, blank=True)  # e.g. 'PO','SO','XFER','ADJ','COUNT'
    reference_id = models.UUIDField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                   related_name='stock_transactions_created')
    note = models.TextField(blank=True)
    balance_after = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True,
                                        help_text="Inventory balance after this transaction (cached)")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["product", "store", "created_at"]),
            models.Index(fields=["reference_type", "reference_id"]),
        ]
        # Prevent duplicate external refs; multiple NULLs allowed in PostgreSQL
        constraints = [
            models.UniqueConstraint(fields=["reference_type", "reference_id"], name="uniq_stock_reference_pair"),
        ]

    def __str__(self):
        return f"{self.product.sku} {self.quantity} ({self.get_movement_type_display()}) @ {self.store.name}"

    @staticmethod
    def _get_inventory_row(product, store, for_update=True):
        """
        Helper to obtain Inventory row with or without select_for_update.
        """
        qs = Inventory.objects.filter(product=product, store=store)
        if for_update:
            return qs.select_for_update().first()
        return qs.first()

    @staticmethod
    def _validate_movement_sign(movement_type, quantity):
        """
        Enforce clean sign conventions.
        """
        q = Decimal(quantity)
        if q == 0:
            raise ValidationError("Quantity (delta) cannot be zero.")
        if movement_type in (MovementType.RECEIPT, MovementType.TRANSFER_IN) and q <= 0:
            raise ValidationError("Quantity must be > 0 for RECEIPT/TRANSFER_IN.")
        if movement_type in (MovementType.ISSUE, MovementType.TRANSFER_OUT) and q >= 0:
            raise ValidationError("Quantity must be < 0 for ISSUE/TRANSFER_OUT.")

    @classmethod
    def create_transaction(cls, product, store, quantity, created_by, unit_cost=None,
                           movement_type=MovementType.RECEIPT, reference_type=None, reference_id=None, note=""):
        """
        Atomic creation of a StockTransaction + update Inventory.quantity (cached).
        Positive quantity = increase stock, negative = decrease stock.
        """
        qty = Decimal(quantity)
        cls._validate_movement_sign(movement_type, qty)

        with transaction.atomic():
            inv = cls._get_inventory_row(product, store, for_update=True)
            if not inv:
                inv = Inventory.objects.create(product=product, store=store, quantity=Decimal("0"))

            new_balance = (inv.quantity or Decimal("0")) + qty
            if new_balance < 0:
                raise ValidationError("Insufficient stock to perform transaction.")

            tx = cls.objects.create(
                product=product,
                store=store,
                quantity=qty,
                unit_cost=unit_cost,
                movement_type=movement_type,
                reference_type=reference_type,
                reference_id=reference_id,
                created_by=created_by,
                note=note,
                balance_after=new_balance,
            )

            inv.quantity = new_balance
            inv.save(update_fields=["quantity", "updated_at"])

            return tx
