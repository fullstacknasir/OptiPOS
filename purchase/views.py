from drf_spectacular.utils import extend_schema
from rest_framework.viewsets import ModelViewSet

from purchase.models import Supplier, PurchaseOrder
from purchase.serializer import SupplierSerializer, PurchaseOrderSerializer


# Create your views here.
@extend_schema(tags=['Supplier'])
class SupplierAPIView(ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer


@extend_schema(tags=['Purchase Order'])
class PurchaseOrderAPIView(ModelViewSet):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
