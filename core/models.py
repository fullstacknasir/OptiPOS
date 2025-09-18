import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


# Create your models here.
class Store(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='store_creator')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class StoreUser(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    user = models.ForeignKey('user.User', on_delete=models.CASCADE)
    is_manager = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("store", "user"),)
        indexes = [models.Index(fields=["store", "user"])]

    def __str__(self):
        return f"{self.user.username} @ {self.store.name}"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='images/category/', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Categories'
        verbose_name = 'Category'

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='images/brand/', null=True, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sku = models.CharField(max_length=100, db_index=True)
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='products')
    description = models.TextField(blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    tax_method = models.CharField(max_length=100, choices=(('inclusive', 'inclusive'), ('exclusive', 'exclusive')))
    tax_rate = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    image = models.ImageField(upload_to='images/product/', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["sku"], name="unique_product_sku")
        ]
        indexes = [
            models.Index(fields=["sku"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name

#
# class MovementType(models.TextChoices):
#     RECEIPT = "RECEIPT", "Receipt"
#     ISSUE = "ISSUE", "Issue"
#     TRANSFER = "TRANSFER", "Transfer"
#     ADJUST = "ADJUST", "Adjust"
#     COUNT = "COUNT", "Stocktake"
#
#
# class Transfer(models.Model):
#     from_store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='transfer_from')
#     to_store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='transfer_to')
#     quantity = models.PositiveIntegerField()
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='transfer_product')
#     type = models.CharField(max_length=16, choices=MovementType.choices)
#     ref_type = models.CharField(max_length=24)  # "PO","RCPT","SO","SHIP","ADJ","XFER","COUNT"
#     ref_id = models.UUIDField()  # links to header doc
#     created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
#     note = models.TextField(blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         indexes = [models.Index(fields=["product", "created_at"])]
#
#     def __str__(self):
#         return self.from_store.name
