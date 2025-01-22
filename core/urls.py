from rest_framework import routers

from core.views import StoreAPIView, CategoryAPIView, BrandAPIView, ProductAPIView, InventoryAPIView, AdjustmentAPIView

app_name = 'core'
router = routers.DefaultRouter()
router.register('store', StoreAPIView, basename='store')
router.register('category', CategoryAPIView, basename='category')
router.register('brand', BrandAPIView, basename='brand')
router.register('product', ProductAPIView, basename='product')
router.register('inventory', InventoryAPIView, basename='inventory')
router.register('adjustment', AdjustmentAPIView, basename='adjustment')
urlpatterns = router.urls
