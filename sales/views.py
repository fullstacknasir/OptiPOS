from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework.viewsets import ModelViewSet

from sales.models import Customer, Sales, SalesLine, Payment
from sales.serializer import CustomerSerializer, SalesSerializer, SalesItemSerializer, TransactionSerializer


# Create your views here.
@extend_schema(tags=['Customer'])
class CustomerAPIView(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


@extend_schema(tags=['Sales'])
class SalesAPIView(ModelViewSet):
    queryset = Sales.objects.all()
    serializer_class = SalesSerializer

@extend_schema(tags=['Sales Item'])
class SalesItemAPIView(ModelViewSet):
    queryset = SalesLine.objects.all()
    serializer_class = SalesItemSerializer


@extend_schema(tags=['Transaction'])
class TransactionAPIView(ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = TransactionSerializer
