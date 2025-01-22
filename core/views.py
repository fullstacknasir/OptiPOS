from rest_framework.viewsets import ModelViewSet

from core.models import Store, Category, Brand, Product, Inventory, Adjustment
from core.serializer import StoreSerializer, CategorySerializer, BrandSerializer, ProductSerializer, \
    InventorySerializer, AdjustmentSerializer


# Create your views here.
class StoreAPIView(ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer


class CategoryAPIView(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class BrandAPIView(ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


class ProductAPIView(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class InventoryAPIView(ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer


class AdjustmentAPIView(ModelViewSet):
    queryset = Adjustment.objects.all()
    serializer_class = AdjustmentSerializer
