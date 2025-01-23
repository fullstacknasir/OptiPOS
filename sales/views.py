from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet

from sales.models import Customer, Sales, SalesItem, Transaction
from sales.serializer import CustomerSerializer, SalesSerializer, SalesItemSerializer, TransactionSerializer


# Create your views here.
class CustomerAPIView(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class SalesAPIView(ModelViewSet):
    queryset = Sales.objects.all()
    serializer_class = SalesSerializer


class SalesItemAPIView(ModelViewSet):
    queryset = SalesItem.objects.all()
    serializer_class = SalesItemSerializer


class TransactionAPIView(ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
