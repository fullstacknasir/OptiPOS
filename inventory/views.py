from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from inventory.models import Inventory, StockTransaction
from inventory.serializer import InventorySerializer, StockTransactionCreateSerializer, StockTransactionReadSerializer


@extend_schema(tags=['Inventory'])
class InventoryViewSet(ModelViewSet):
    """CRUD for inventory rows."""
    queryset = Inventory.objects.select_related("product", "store").all()
    serializer_class = InventorySerializer
    # filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # filterset_fields = ["store", "product", "is_active"]
    search_fields = ["product__name", "store__name"]
    ordering_fields = ["updated_at", "quantity", "stock_alert"]
    ordering = ["-updated_at"]


@extend_schema(tags=['Stock Transactions'])
class StockTransactionViewSet(mixins.CreateModelMixin,
                              mixins.RetrieveModelMixin,
                              mixins.ListModelMixin,
                              GenericViewSet):
    """Immutable ledger: create + read only."""
    queryset = StockTransaction.objects.select_related("product", "store", "created_by").all()
    # filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # filterset_fields = ["product", "store", "movement_type", "created_by", "reference_type", "reference_id"]
    search_fields = ["note", "product__name", "store__name", "reference_type"]
    ordering_fields = ["created_at", "quantity", "movement_type"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        return StockTransactionCreateSerializer if self.action == "create" else StockTransactionReadSerializer

    # block updates/deletes to keep audit log immutable
    def update(self, request, *args, **kwargs):
        return Response({"detail": "Method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response({"detail": "Method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "Method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)