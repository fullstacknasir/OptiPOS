from rest_framework import routers

from purchase.views import SupplierAPIView, PurchaseOrderAPIView, PurchasedItemAPIView

app_name = 'purchase'
router = routers.DefaultRouter()
router.register('supplier', SupplierAPIView, basename='supplier')
router.register('purchase', PurchaseOrderAPIView, basename='purchase')
router.register('purchase_item', PurchasedItemAPIView, basename='purchase_item')
urlpatterns = router.urls
