from rest_framework import serializers
from sales.models import Customer, Sales, SalesLine, Payment


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ('id',)


class SalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sales
        fields = '__all__'
        read_only_fields = ('id',)


class SalesItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesLine
        fields = '__all__'
        read_only_fields = ('id',)


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('id',)