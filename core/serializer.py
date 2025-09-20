from rest_framework import serializers

from core.models import Store, Category, Brand, Product, StoreUser
from user.serializer import UserSerializer


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'
        read_only_fields = ('id', 'creator')


class StoreUserViewSerializer(serializers.ModelSerializer):
    store = StoreSerializer(many=False)
    user = UserSerializer(many=False)

    class Meta:
        model = StoreUser
        fields = '__all__'
        read_only_fields = ('id',)


class StoreUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreUser
        fields = '__all__'
        read_only_fields = ('id',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('id',)


class BrandSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = Brand
        fields = '__all__'
        read_only_fields = ('id',)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('id',)
