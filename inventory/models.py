import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models, transaction

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
        unique_together = (("product", "store"),)
        indexes = [models.Index(fields=["product", "store"])]
        verbose_name_plural = 'Inventory'
        verbose_name = 'Inventory'

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
        indexes = [
            models.Index(fields=["product", "store", "created_at"]),
            models.Index(fields=["reference_type", "reference_id"])
        ]
        ordering = ["-created_at"]

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

    @classmethod
    def create_transaction(cls, product, store, quantity, created_by, unit_cost=None,
                           movement_type=MovementType.RECEIPT, reference_type=None, reference_id=None, note=""):
        """
        Atomic creation of a StockTransaction + update Inventory.quantity (cached).
        Positive quantity = increase stock, negative = decrease stock.
        """
        with transaction.atomic():
            inv = cls._get_inventory_row(product, store, for_update=True)
            if not inv:
                inv = Inventory.objects.create(product=product, store=store, quantity=0)
            # compute new balance
            new_balance = (inv.quantity or 0) + quantity
            if new_balance < 0:
                raise ValueError("Insufficient stock to perform transaction (would go negative).")
            tx = cls.objects.create(
                product=product,
                store=store,
                quantity=quantity,
                unit_cost=unit_cost,
                movement_type=movement_type,
                reference_type=reference_type,
                reference_id=reference_id,
                created_by=created_by,
                note=note,
                balance_after=new_balance
            )
            # update cached inventory
            inv.quantity = new_balance
            inv.save(update_fields=["quantity", "updated_at"])
            return tx
