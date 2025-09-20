from django.shortcuts import redirect
from django.views import View
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.models import Store, Category, Brand, Product, StoreUser
from core.serializer import StoreSerializer, CategorySerializer, BrandSerializer, ProductSerializer, \
    StoreUserViewSerializer, StoreUserSerializer


# Create your views here.
class IndexView(View):
    def get(self, request):
        return redirect('/docs')


@extend_schema(tags=['Store'])
class StoreAPIView(ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


@extend_schema(tags=['Store User'])
class StoreUserAPIView(ModelViewSet):
    queryset = StoreUser.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return StoreUserViewSerializer
        return StoreUserSerializer


@extend_schema(tags=['Category'])
class CategoryAPIView(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    parser_classes = (MultiPartParser, FormParser)

    @extend_schema(
        tags=['Category'],
        parameters=[
            OpenApiParameter(name="search", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY,
                             description="Filter products by name", required=False),
        ],
        responses=ProductSerializer(many=True),
    )
    @action(detail=True, methods=['get'], serializer_class=ProductSerializer)
    def product(self, request, pk=None):
        cat = self.get_object()
        queryset = cat.products.all()
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=['Brand'],
               request={'multipart/form-data': BrandSerializer})
class BrandAPIView(ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        tags=['Brand'],
        parameters=[
            OpenApiParameter(name="search", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY,
                             description="Filter products by name", required=False),
        ],
        responses=ProductSerializer(many=True),
    )
    @action(detail=True, methods=['get'], serializer_class=ProductSerializer)
    def product(self, request, pk=None):
        cat = self.get_object()
        queryset = cat.products.all()
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=['Products'])
class ProductAPIView(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser]


    @extend_schema(
        parameters=[
            OpenApiParameter(name="search", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY,
                             description="Filter products by name", required=False),
        ],
        responses=ProductSerializer(many=True),
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset();
        if request.query_params.get('search'):
            queryset = queryset.filter(name__icontains=request.query_params.get('search'))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        return Response(ProductSerializer(queryset, many=True).data, status=status.HTTP_200_OK)