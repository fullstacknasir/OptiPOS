from rest_framework import routers

from core.views import StoreAPIView, CategoryAPIView, BrandAPIView, ProductAPIView, InventoryAPIView, AdjustmentAPIView
from sales.views import CustomerAPIView, SalesAPIView, SalesItemAPIView, TransactionAPIView

app_name = 'sales'
router = routers.DefaultRouter()
router.register('customer', CustomerAPIView, basename='customer')
router.register('sales', SalesAPIView, basename='sales')
router.register('sales_item', SalesItemAPIView, basename='sales_item')
router.register('transaction', TransactionAPIView, basename='transaction')
urlpatterns = router.urls
