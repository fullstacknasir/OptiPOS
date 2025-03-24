
from django.db import models

from user.models import User


# Create your models here.
class Store(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='store_creator')

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='images/category/')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'
        verbose_name = 'Category'


class Brand(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='images/brand/')

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    sku = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    tax_method = models.CharField(max_length=100, choices=(('inclusive', 'inclusive'), ('exclusive', 'exclusive')))
    tax_rate = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='images/product/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='inventory')
    quantity = models.IntegerField()
    stock_alert = models.IntegerField()
    discount_method = models.CharField(max_length=100, choices=(('percentage', 'percentage'), ('flat', 'flat')))
    discount_rate = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.name

    class Meta:
        verbose_name_plural = 'Inventory'
        verbose_name = 'Inventory'


class Adjustment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='adjustments')
    quantity = models.IntegerField()
    type = models.CharField(max_length=100, choices=(('Addition', 'Addition'), ('Subtraction', 'Subtraction')))
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.name


class Transfer(models.Model):
    from_store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='transfer_from')
    to_store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='transfer_to')
    quantity = models.PositiveIntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='transfer_product')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.from_store.name
