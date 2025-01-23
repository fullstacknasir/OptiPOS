from rest_framework import routers

from user.views import CreateUserAPIView, SetPasswordAPIView

app_name = 'user'
router = routers.DefaultRouter()
router.register('user', CreateUserAPIView, basename='user')
router.register(r'set-password/(?P<uid>[^/.]+)/(?P<token>[^/.]+)', SetPasswordAPIView, basename='set-password')
urlpatterns = router.urls
