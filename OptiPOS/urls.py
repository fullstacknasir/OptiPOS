"""
URL configuration for OptiPOS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

schema_view = get_schema_view(
    openapi.Info(
        title="Inventory Management API",
        default_version='v1',
        description="API documentation for the Inventory Management System",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny, ],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('rest_framework.urls', namespace='rest_framework')),
    path('v1/api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('v1/api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('v1/api/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('v1/api/auth/', include('user.urls', namespace='user')),
    path('v1/api/', include('core.urls', namespace='core')),
    path('v1/api/', include('sales.urls', namespace='sales')),
    path('v1/api/', include('purchase.urls', namespace='purchase')),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
