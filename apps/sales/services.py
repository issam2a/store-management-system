from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.products.models import Product
from apps.transactions.models import TransactionCancellation

from .models import Sale, SaleItem


TWO_PLACES = Decimal("0.01")

VALUE_BASED_UNIT_SYMBOLS = {
    "kg",
    "g",
    "l",
    "ml",
}

def generate_sale_reference():
    """
    Generate a human-readable unique sale reference.

    V1 approach:
    SALE-000001
    SALE-000002
    ...
    """
    last_sale = Sale.objects.order_by("-id").first()

    if last_sale is None:
        next_number = 1
    else:
        next_number = last_sale.id + 1

    return f"SALE-{next_number:06d}"


def _quantize_money(value):
    """
    Normalize monetary values to two decimal places.
    """
    return Decimal(value).quantize(
        TWO_PLACES,
        rounding=ROUND_HALF_UP,
    )


def recalculate_sale_total(sale):
    subtotal = sum(
        (
            item.line_total
            for item in sale.items.all()
        ),
        Decimal("0.00"),
    )

    subtotal = _quantize_money(subtotal)

    discount = _quantize_money(
        sale.discount_amount or Decimal("0.00")
    )

    if discount < Decimal("0.00"):
        raise ValidationError(
            "Discount cannot be negative."
        )

    if discount > subtotal:
        raise ValidationError(
            "Discount cannot exceed the sale subtotal."
        )

    total = _quantize_money(
        subtotal - discount
    )

    sale.subtotal_amount = subtotal
    sale.discount_amount = discount
    sale.total_amount = total

    sale.save(
        update_fields=[
            "subtotal_amount",
            "discount_amount",
            "total_amount",
        ]
    )

    return sale

def create_sale(
    *,
    customer,
    payment_type,
    user,
):
    """
    Create a new draft sale.

    Draft creation does not affect inventory.
    """

    if payment_type not in {
        Sale.PaymentType.CASH,
        Sale.PaymentType.CREDIT,
    }:
        raise ValidationError(
            "Invalid payment type."
        )

    if (
        payment_type == Sale.PaymentType.CREDIT
        and customer is None
    ):
        raise ValidationError(
            "A credit sale requires a customer."
        )

    sale = Sale.objects.create(
        reference=generate_sale_reference(),
        customer=customer,
        payment_type=payment_type,
        status=Sale.Status.DRAFT,
        subtotal_amount=Decimal("0.00"),
        discount_amount=Decimal("0.00"),
        total_amount=Decimal("0.00"),
        created_by=user,
    )

    return sale


def add_sale_item(
    *,
    sale_id,
    product,
    quantity=None,
    amount=None,
):
    with transaction.atomic():
        sale = (
            Sale.objects
            .select_for_update()
            .get(pk=sale_id)
        )

        if sale.status != Sale.Status.DRAFT:
            raise ValidationError(
                "Only draft sales can be modified."
            )

        product = (
            Product.objects
            .select_for_update()
            .select_related("unit")
            .get(pk=product.id)
        )

        if not product.is_active:
            raise ValidationError(
                f"Product '{product.name}' is inactive."
            )

        if product.current_sell_price <= Decimal("0.00"):
            raise ValidationError(
                f"Product '{product.name}' does not have a valid selling price."
            )

        unit_symbol = product.unit.symbol.strip().lower()

        if unit_symbol in VALUE_BASED_UNIT_SYMBOLS:
            if amount is None:
                raise ValidationError(
                    "An amount is required for this product."
                )

            amount = _quantize_money(amount)

            if amount <= Decimal("0.00"):
                raise ValidationError(
                    "Amount must be greater than zero."
                )

            unit_price = _quantize_money(
                product.current_sell_price
            )

            quantity = amount / unit_price

            quantity = quantity.quantize(
                Decimal("0.001"),
                rounding=ROUND_HALF_UP,
            )

            if quantity <= Decimal("0.000"):
                raise ValidationError(
                    "The amount is too small to create a valid quantity."
                )

            line_total = amount

        else:
            if quantity is None:
                raise ValidationError(
                    "A quantity is required for this product."
                )

            quantity = Decimal(quantity)

            if quantity <= Decimal("0.000"):
                raise ValidationError(
                    "Quantity must be greater than zero."
                )

            unit_price = _quantize_money(
                product.current_sell_price
            )

            line_total = _quantize_money(
                quantity * unit_price
            )

        if product.current_stock < quantity:
            raise ValidationError(
                f"Insufficient stock for '{product.name}'. "
                f"Available: {product.current_stock} {product.unit.symbol}, "
                f"requested: {quantity} {product.unit.symbol}."
            )

        existing_item = (
            sale.items
            .filter(product=product)
            .first()
        )

        if existing_item is not None:
            raise ValidationError(
                f"'{product.name}' is already in this sale. "
                "Update its quantity instead."
            )

        item = SaleItem.objects.create(
            sale=sale,
            product=product,
            quantity=quantity,
            unit_price=unit_price,
            line_total=line_total,
            unit_cost=Decimal("0.00"),
        )

        recalculate_sale_total(sale)

        return item


def update_sale_item(
    *,
    item_id,
    quantity,
):
    """
    Update the quantity of an existing draft sale item.

    The historical selling price is preserved.

    Inventory is not modified.
    """

    quantity = Decimal(quantity)

    if quantity <= Decimal("0.000"):
        raise ValidationError(
            "Quantity must be greater than zero."
        )

    with transaction.atomic():

        item = (
            SaleItem.objects
            .select_for_update()
            .select_related("sale", "product")
            .get(pk=item_id)
        )

        sale = item.sale

        if sale.status != Sale.Status.DRAFT:
            raise ValidationError(
                "Only draft sales can be modified."
            )

        product = (
            Product.objects
            .select_for_update()
            .get(pk=item.product_id)
        )

        if product.current_stock < quantity:
            raise ValidationError(
                f"Insufficient stock for '{product.name}'. "
                f"Available: {product.current_stock}, "
                f"requested: {quantity}."
            )

        item.quantity = quantity

        item.line_total = _quantize_money(
            quantity * item.unit_price
        )

        item.save(
            update_fields=[
                "quantity",
                "line_total",
            ]
        )

        recalculate_sale_total(sale)

        return item


def remove_sale_item(
    item_id,
):
    """
    Remove an item from a draft sale.

    Inventory is not affected.
    """

    with transaction.atomic():

        item = (
            SaleItem.objects
            .select_for_update()
            .select_related("sale")
            .get(pk=item_id)
        )

        sale = item.sale

        if sale.status != Sale.Status.DRAFT:
            raise ValidationError(
                "Only draft sales can be modified."
            )

        item.delete()

        recalculate_sale_total(sale)

        return sale


def set_sale_discount(*, sale_id, discount_amount):
    discount_amount = _quantize_money(
        discount_amount or Decimal("0.00")
    )

    if discount_amount < Decimal("0.00"):
        raise ValidationError(
            "Discount cannot be negative."
        )

    with transaction.atomic():
        sale = (
            Sale.objects
            .select_for_update()
            .get(pk=sale_id)
        )

        if sale.status != Sale.Status.DRAFT:
            raise ValidationError(
                "Only draft sales can be modified."
            )

        subtotal = sum(
            (
                item.line_total
                for item in sale.items.all()
            ),
            Decimal("0.00"),
        )

        subtotal = _quantize_money(subtotal)

        if discount_amount > subtotal:
            raise ValidationError(
                "Discount cannot exceed the sale subtotal."
            )

        total = _quantize_money(
            subtotal - discount_amount
        )

        sale.subtotal_amount = subtotal
        sale.discount_amount = discount_amount
        sale.total_amount = total

        sale.save(
            update_fields=[
                "subtotal_amount",
                "discount_amount",
                "total_amount",
            ]
        )

        return sale


def complete_sale(
    *,
    sale_id,
    user,
):
    """
    Complete a draft sale.

    Business effects:
    - validate sale state
    - validate customer/payment rules
    - validate sale contains items
    - validate stock
    - snapshot current purchase cost
    - deduct inventory
    - finalize sale totals
    - mark sale completed

    All changes occur atomically.
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

        items = list(
            sale.items
            .select_related("product")
            .select_for_update()
        )

        if not items:
            raise ValidationError(
                "A sale must contain at least one item."
            )

        if (
            sale.payment_type == Sale.PaymentType.CREDIT
            and sale.customer_id is None
        ):
            raise ValidationError(
                "A credit sale requires a customer."
            )

        # Defense against duplicate products.
        product_ids = [
            item.product_id
            for item in items
        ]

        if len(product_ids) != len(set(product_ids)):
            raise ValidationError(
                "A sale cannot contain the same product more than once."
            )

        # Recalculate from the actual items before completion.
        subtotal = sum(
            (
                item.line_total
                for item in items
            ),
            Decimal("0.00"),
        )

        subtotal = _quantize_money(subtotal)

        discount = _quantize_money(
            sale.discount_amount or Decimal("0.00")
        )

        if discount < Decimal("0.00"):
            raise ValidationError(
                "Discount cannot be negative."
            )

        if discount > subtotal:
            raise ValidationError(
                "Discount cannot exceed the sale subtotal."
            )

        total = _quantize_money(
            subtotal - discount
        )

        # Validate every product before modifying any inventory.
        for item in items:

            product = item.product

            if not product.is_active:
                raise ValidationError(
                    f"Product '{product.name}' is inactive."
                )

            if product.current_stock < item.quantity:
                raise ValidationError(
                    f"Insufficient stock for '{product.name}'. "
                    f"Available: {product.current_stock}, "
                    f"requested: {item.quantity}."
                )

            if product.current_purchase_cost is None:
                raise ValidationError(
                    f"Product '{product.name}' does not have "
                    "a current purchase cost."
                )

        # All validation has passed.
        #
        # Now apply the inventory and historical cost snapshots.
        for item in items:

            product = item.product

            item.unit_cost = _quantize_money(
                product.current_purchase_cost
            )

            item.save(
                update_fields=[
                    "unit_cost",
                ]
            )

            product.current_stock -= item.quantity

            product.save(
                update_fields=[
                    "current_stock",
                    "updated_at",
                ]
            )

        sale.subtotal_amount = subtotal
        sale.total_amount = total
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


def cancel_sale(
    *,
    sale_id,
    user,
    reason,
):
    """
    Cancel a completed sale.

    Cancellation:
    - preserves the original sale
    - records cancellation audit information
    - restores inventory
    - marks the sale CANCELLED

    The sale is never deleted.
    """

    reason = (reason or "").strip()

    if not reason:
        raise ValidationError(
            "A cancellation reason is required."
        )

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

        items = list(
            sale.items
            .select_related("product")
            .select_for_update()
        )

        # Lock products and validate the reversal.
        for item in items:

            product = (
                Product.objects
                .select_for_update()
                .get(pk=item.product_id)
            )

            product.current_stock += item.quantity

            product.save(
                update_fields=[
                    "current_stock",
                    "updated_at",
                ]
            )

        # Record the cancellation audit event.
        TransactionCancellation.objects.create(
            sale=sale,
            reason=reason,
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

        return sale