from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.viewsets import ModelViewSet

from core.models import Store, Category, Brand, Product, StoreUser
from core.serializer import StoreSerializer, CategorySerializer, BrandSerializer, ProductSerializer, \
    StoreUserViewSerializer, StoreUserSerializer


# Create your views here.
class StoreAPIView(ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer


class StoreUserAPIView(ModelViewSet):
    queryset = StoreUser.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return StoreUserViewSerializer
        return StoreUserSerializer


class CategoryAPIView(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    parser_classes = (MultiPartParser, FormParser)


class BrandAPIView(ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    parser_classes = (MultiPartParser, FormParser)


class ProductAPIView(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = (MultiPartParser, FormParser)
