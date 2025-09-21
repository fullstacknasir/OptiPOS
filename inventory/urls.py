from rest_framework import routers

from inventory.views import InventoryViewSet, StockTransactionViewSet

app_name = 'inventory'
router = routers.DefaultRouter()

router.register(r"inventory", InventoryViewSet, basename="inventory")
router.register(r"stock-transactions", StockTransactionViewSet, basename="stocktransaction")

urlpatterns = router.urls
