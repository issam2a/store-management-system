from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.products.models import Product

from .models import InventoryAdjustment


def apply_inventory_adjustment(adjustment_id, user):
    with transaction.atomic():
        adjustment = (
            InventoryAdjustment.objects
            .select_for_update()
            .select_related("product")
            .get(pk=adjustment_id)
        )

        product = (
            Product.objects
            .select_for_update()
            .get(pk=adjustment.product_id)
        )

        if adjustment.quantity <= Decimal("0"):
            raise ValidationError(
                "Adjustment quantity must be greater than zero."
            )

        if adjustment.adjustment_type == (
            InventoryAdjustment.AdjustmentType.INCREASE
        ):
            product.current_stock += adjustment.quantity

        elif adjustment.adjustment_type == (
            InventoryAdjustment.AdjustmentType.DECREASE
        ):
            if product.current_stock < adjustment.quantity:
                raise ValidationError(
                    f"Cannot decrease stock for '{product.name}'. "
                    f"Available: {product.current_stock}, "
                    f"requested: {adjustment.quantity}."
                )

            product.current_stock -= adjustment.quantity

        else:
            raise ValidationError(
                "Invalid inventory adjustment type."
            )

        product.save(
            update_fields=[
                "current_stock",
                "updated_at",
            ]
        )

        return adjustment