from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.products.models import Product
from apps.transactions.models import TransactionCancellation

from .models import Sale


def complete_sale(sale_id, user):
    """
    Complete a draft sale.

    Business effects:
    - Validate the sale state and payment rules.
    - Calculate line totals and subtotal.
    - Validate the discount.
    - Validate sufficient stock.
    - Reduce product stock.
    - Store the final sale totals.
    - Mark the sale as COMPLETED.
    """

    with transaction.atomic():
        sale = (
            Sale.objects
            .select_for_update()
            .get(pk=sale_id)
        )

        if sale.status != Sale.Status.DRAFT:
            raise ValidationError(
                "Only draft sales can be completed."
            )

        if (
            sale.payment_type == Sale.PaymentType.CREDIT
            and sale.customer_id is None
        ):
            raise ValidationError(
                "A credit sale requires a customer."
            )

        items = list(
            sale.items
            .select_related("product")
            .order_by("product_id")
        )

        if not items:
            raise ValidationError(
                "A sale must contain at least one item."
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

        subtotal_amount = Decimal("0.00")

        # Calculate totals and validate stock before modifying anything.
        for item in items:
            product = products.get(item.product_id)

            if product is None:
                raise ValidationError(
                    f"Product {item.product_id} does not exist."
                )

            if product.current_stock < item.quantity:
                raise ValidationError(
                    f"Insufficient stock for '{product.name}'. "
                    f"Available: {product.current_stock}, "
                    f"requested: {item.quantity}."
                )

            line_total = (
                item.quantity * item.unit_price
            ).quantize(Decimal("0.01"))

            item.line_total = line_total
            subtotal_amount += line_total

        discount_amount = sale.discount_amount or Decimal("0.00")

        if discount_amount < Decimal("0.00"):
            raise ValidationError(
                "Discount cannot be negative."
            )

        if discount_amount > subtotal_amount:
            raise ValidationError(
                "Discount cannot exceed the sale subtotal."
            )

        total_amount = (
            subtotal_amount - discount_amount
        ).quantize(Decimal("0.01"))

        # Apply item updates and reduce stock.
        for item in items:
            item.save(update_fields=["line_total"])

            product = products[item.product_id]

            product.current_stock -= item.quantity
            product.save(
                update_fields=[
                    "current_stock",
                    "updated_at",
                ]
            )

        sale.subtotal_amount = subtotal_amount
        sale.total_amount = total_amount
        sale.status = Sale.Status.COMPLETED
        sale.completed_at = timezone.now()
        sale.completed_by = user

        sale.save(
            update_fields=[
                "subtotal_amount",
                "total_amount",
                "status",
                "completed_at",
                "completed_by",
            ]
        )

        return sale


def cancel_sale(sale_id, user, reason):
    """
    Cancel a completed sale.

    Business effects:
    - Reverse the sale's inventory reduction.
    - Create a transaction cancellation record.
    - Mark the sale as CANCELLED.
    """

    with transaction.atomic():
        sale = (
            Sale.objects
            .select_for_update()
            .get(pk=sale_id)
        )

        if sale.status != Sale.Status.COMPLETED:
            raise ValidationError(
                "Only completed sales can be cancelled."
            )

        if not reason or not reason.strip():
            raise ValidationError(
                "A cancellation reason is required."
            )

        if (
            TransactionCancellation.objects
            .filter(sale=sale)
            .exists()
        ):
            raise ValidationError(
                "This sale has already been cancelled."
            )

        items = list(
            sale.items
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

        # Validate that all products exist before changing stock.
        for item in items:
            product = products.get(item.product_id)

            if product is None:
                raise ValidationError(
                    f"Product {item.product_id} does not exist."
                )

        # Reverse the inventory reduction.
        for item in items:
            product = products[item.product_id]

            product.current_stock += item.quantity
            product.save(
                update_fields=[
                    "current_stock",
                    "updated_at",
                ]
            )

        cancellation = TransactionCancellation.objects.create(
            sale=sale,
            reason=reason.strip(),
            cancelled_by=user,
        )

        sale.status = Sale.Status.CANCELLED
        sale.cancelled_at = timezone.now()
        sale.cancelled_by = user

        sale.save(
            update_fields=[
                "status",
                "cancelled_at",
                "cancelled_by",
            ]
        )

        return sale, cancellation