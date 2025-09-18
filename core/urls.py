from rest_framework import routers

from core.views import StoreAPIView, CategoryAPIView, BrandAPIView, ProductAPIView, StoreUserAPIView

app_name = 'core'
router = routers.DefaultRouter()
router.register('store', StoreAPIView, basename='store')
router.register('store-user', StoreUserAPIView, basename='store-user')
router.register('category', CategoryAPIView, basename='category')
router.register('brand', BrandAPIView, basename='brand')
router.register('product', ProductAPIView, basename='product')
urlpatterns = router.urls
