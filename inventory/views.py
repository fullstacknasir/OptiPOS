from drf_spectacular.utils import extend_schema
from rest_framework.viewsets import ModelViewSet

from inventory.models import Inventory
from inventory.serializer import InventorySerializer


# Create your views here.

@extend_schema(tags=['Inventory'])
class InventoryAPIView(ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
