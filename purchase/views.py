from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet

from purchase.models import Supplier, PurchaseOrder, PurchasedItem
from purchase.serializer import SupplierSerializer, PurchaseOrderSerializer, PurchasedItemSerializer


# Create your views here.

class SupplierAPIView(ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer


class PurchaseOrderAPIView(ModelViewSet):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer


class PurchasedItemAPIView(ModelViewSet):
    queryset = PurchasedItem.objects.all()
    serializer_class = PurchasedItemSerializer
