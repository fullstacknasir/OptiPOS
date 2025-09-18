from rest_framework import routers

from purchase.views import SupplierAPIView, PurchaseOrderAPIView

app_name = 'purchase'
router = routers.DefaultRouter()
router.register('supplier', SupplierAPIView, basename='supplier')
router.register('purchase', PurchaseOrderAPIView, basename='purchase')
urlpatterns = router.urls
