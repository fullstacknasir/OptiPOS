from rest_framework import serializers

from inventory.models import Inventory, StockTransaction, MovementType

ProductModel = Inventory._meta.get_field("product").remote_field.model
StoreModel = Inventory._meta.get_field("store").remote_field.model
class InventorySerializer(serializers.ModelSerializer):
    # readonly denorm fields
    product_name = serializers.CharField(source="product.name", read_only=True)
    store_name = serializers.CharField(source="store.name", read_only=True)

    class Meta:
        model = Inventory
        fields = [
            "id", "product", "product_name", "store", "store_name",
            "quantity", "stock_alert", "discount_method", "discount_rate",
            "is_active", "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class StockTransactionReadSerializer(serializers.ModelSerializer):
    # readable extras
    product_name = serializers.CharField(source="product.name", read_only=True)
    store_name = serializers.CharField(source="store.name", read_only=True)
    movement_type_display = serializers.CharField(source="get_movement_type_display", read_only=True)

    class Meta:
        model = StockTransaction
        fields = [
            "id", "created_at",
            "product", "product_name",
            "store", "store_name",
            "quantity", "unit_cost",
            "movement_type", "movement_type_display",
            "reference_type", "reference_id",
            "created_by", "note", "balance_after",
        ]


class StockTransactionCreateSerializer(serializers.Serializer):
    # create-only payload (delta-based)
    product = serializers.PrimaryKeyRelatedField(queryset=ProductModel.objects.all())
    store = serializers.PrimaryKeyRelatedField(queryset=StoreModel.objects.all())
    quantity = serializers.DecimalField(max_digits=18, decimal_places=6)  # signed delta
    movement_type = serializers.ChoiceField(choices=MovementType.choices, default=MovementType.ADJUST)
    unit_cost = serializers.DecimalField(max_digits=14, decimal_places=4, required=False, allow_null=True)
    reference_type = serializers.CharField(max_length=32, required=False, allow_blank=True)
    reference_id = serializers.UUIDField(required=False, allow_null=True)
    note = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        # early sign rules; model method re-validates
        StockTransaction._validate_movement_sign(attrs["movement_type"], attrs["quantity"])
        return attrs

    def create(self, validated):
        # atomic ledger + inventory update
        user = getattr(getattr(self.context, "get", lambda k: None)("request"), "user", None)
        tx = StockTransaction.create_transaction(
            product=validated["product"],
            store=validated["store"],
            quantity=validated["quantity"],
            unit_cost=validated.get("unit_cost"),
            movement_type=validated.get("movement_type", MovementType.ADJUST),
            reference_type=validated.get("reference_type"),
            reference_id=validated.get("reference_id"),
            created_by=user,
            note=validated.get("note", ""),
        )
        return tx