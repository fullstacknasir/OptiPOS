from rest_framework import routers

from inventory.views import InventoryAPIView

app_name = 'inventory'
router = routers.DefaultRouter()
router.register('inventory', InventoryAPIView, basename='inventory')
urlpatterns = router.urls