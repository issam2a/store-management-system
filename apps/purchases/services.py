from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import Purchase
from apps.products.models import Product


def complete_purchase(purchase_id, user):
    """
    Complete a draft purchase.

    Business effects:
    - Calculate line totals and purchase total.
    - Increase product stock.
    - Update current purchase cost.
    - Mark purchase as COMPLETED.
    - Record completion user and timestamp.
    """

    with transaction.atomic():
        purchase = (
            Purchase.objects
            .select_for_update()
            .get(pk=purchase_id)
        )

        if purchase.status != Purchase.Status.DRAFT:
            raise ValidationError(
                "Only draft purchases can be completed."
            )

        items = list(
            purchase.items
            .select_related("product")
            .order_by("product_id")
        )

        if not items:
            raise ValidationError(
                "A purchase must contain at least one item."
            )

        # Lock products in deterministic order.
        product_ids = sorted(
            {item.product_id for item in items}
        )

        products = {
            product.id: product
            for product in (
                Product.objects
                .select_for_update()
                .filter(id__in=product_ids)
                .order_by("id")
            )
        }

        total_amount = Decimal("0.00")

        for item in items:
            product = products.get(item.product_id)

            if product is None:
                raise ValidationError(
                    f"Product {item.product_id} does not exist."
                )

            line_total = (
                item.quantity * item.unit_cost
            ).quantize(Decimal("0.01"))

            item.line_total = line_total
            item.save(update_fields=["line_total"])

            total_amount += line_total

            product.current_stock += item.quantity
            product.current_purchase_cost = item.unit_cost
            product.save(
                update_fields=[
                    "current_stock",
                    "current_purchase_cost",
                    "updated_at",
                ]
            )

        purchase.total_amount = total_amount
        purchase.status = Purchase.Status.COMPLETED
        purchase.completed_at = timezone.now()
        purchase.completed_by = user

        purchase.save(
            update_fields=[
                "total_amount",
                "status",
                "completed_at",
                "completed_by",
            ]
        )

        return purchase


def cancel_purchase(purchase_id, user, reason):
    """
    Cancel a completed purchase.

    Business effects:
    - Reverse the purchase's inventory increase.
    - Prevent stock from becoming negative.
    - Create a transaction cancellation record.
    - Mark the purchase as CANCELLED.
    """

    from apps.transactions.models import TransactionCancellation

    with transaction.atomic():
        purchase = (
            Purchase.objects
            .select_for_update()
            .get(pk=purchase_id)
        )

        if purchase.status != Purchase.Status.COMPLETED:
            raise ValidationError(
                "Only completed purchases can be cancelled."
            )

        if not reason or not reason.strip():
            raise ValidationError(
                "A cancellation reason is required."
            )

        existing_cancellation = (
            TransactionCancellation.objects
            .filter(purchase=purchase)
            .exists()
        )

        if existing_cancellation:
            raise ValidationError(
                "This purchase has already been cancelled."
            )

        items = list(
            purchase.items
            .select_related("product")
            .order_by("product_id")
        )

        product_ids = sorted(
            {item.product_id for item in items}
        )

        products = {
            product.id: product
            for product in (
                Product.objects
                .select_for_update()
                .filter(id__in=product_ids)
                .order_by("id")
            )
        }

        # Validate the complete reversal before changing anything.
        for item in items:
            product = products.get(item.product_id)

            if product is None:
                raise ValidationError(
                    f"Product {item.product_id} does not exist."
                )

            if product.current_stock < item.quantity:
                raise ValidationError(
                    f"Cannot cancel purchase because stock for "
                    f"'{product.name}' would become negative."
                )

        # Apply the inventory reversal.
        for item in items:
            product = products[item.product_id]

            product.current_stock -= item.quantity
            product.save(
                update_fields=[
                    "current_stock",
                    "updated_at",
                ]
            )

        cancellation = TransactionCancellation.objects.create(
            purchase=purchase,
            reason=reason.strip(),
            cancelled_by=user,
        )

        purchase.status = Purchase.Status.CANCELLED
        purchase.cancelled_at = timezone.now()
        purchase.cancelled_by = user

        purchase.save(
            update_fields=[
                "status",
                "cancelled_at",
                "cancelled_by",
            ]
        )

        return purchase, cancellation