from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Category, Product, Unit


@transaction.atomic
def create_category(*, name):
    """
    Create a new product category.

    Business rules:
    - Category names must be unique.
    - New categories are active by default.
    """

    name = name.strip()

    if not name:
        raise ValidationError("Category name is required.")

    if Category.objects.filter(name__iexact=name).exists():
        raise ValidationError(
            "A category with this name already exists."
        )

    return Category.objects.create(
        name=name,
        is_active=True,
    )


@transaction.atomic
def update_category(*, category_id, name):
    """
    Update an existing category.

    The category identity is preserved.
    """

    category = Category.objects.get(pk=category_id)

    name = name.strip()

    if not name:
        raise ValidationError("Category name is required.")

    duplicate = (
        Category.objects
        .filter(name__iexact=name)
        .exclude(pk=category.pk)
        .exists()
    )

    if duplicate:
        raise ValidationError(
            "A category with this name already exists."
        )

    category.name = name
    category.save(update_fields=["name", "updated_at"])

    return category


@transaction.atomic
def deactivate_category(*, category_id):
    """
    Deactivate a category instead of deleting it.

    Existing products may continue referencing the category.
    """

    category = Category.objects.get(pk=category_id)

    category.is_active = False
    category.save(update_fields=["is_active", "updated_at"])

    return category


@transaction.atomic
def activate_category(*, category_id):
    """
    Reactivate a previously deactivated category.
    """

    category = Category.objects.get(pk=category_id)

    category.is_active = True
    category.save(update_fields=["is_active", "updated_at"])

    return category


@transaction.atomic
def create_unit(*, name, symbol):
    """
    Create a new product unit.

    Examples:
    - Piece / pcs
    - Kilogram / kg
    - Box / box
    """

    name = name.strip()
    symbol = symbol.strip()

    if not name:
        raise ValidationError("Unit name is required.")

    if not symbol:
        raise ValidationError("Unit symbol is required.")

    if Unit.objects.filter(name__iexact=name).exists():
        raise ValidationError(
            "A unit with this name already exists."
        )

    if Unit.objects.filter(symbol__iexact=symbol).exists():
        raise ValidationError(
            "A unit with this symbol already exists."
        )

    return Unit.objects.create(
        name=name,
        symbol=symbol,
        is_active=True,
    )


@transaction.atomic
def update_unit(*, unit_id, name, symbol):
    """
    Update an existing unit.
    """

    unit = Unit.objects.get(pk=unit_id)

    name = name.strip()
    symbol = symbol.strip()

    if not name:
        raise ValidationError("Unit name is required.")

    if not symbol:
        raise ValidationError("Unit symbol is required.")

    duplicate_name = (
        Unit.objects
        .filter(name__iexact=name)
        .exclude(pk=unit.pk)
        .exists()
    )

    if duplicate_name:
        raise ValidationError(
            "A unit with this name already exists."
        )

    duplicate_symbol = (
        Unit.objects
        .filter(symbol__iexact=symbol)
        .exclude(pk=unit.pk)
        .exists()
    )

    if duplicate_symbol:
        raise ValidationError(
            "A unit with this symbol already exists."
        )

    unit.name = name
    unit.symbol = symbol

    unit.save(
        update_fields=[
            "name",
            "symbol",
            "updated_at",
        ]
    )

    return unit


@transaction.atomic
def deactivate_unit(*, unit_id):
    """
    Deactivate a unit instead of deleting it.
    """

    unit = Unit.objects.get(pk=unit_id)

    unit.is_active = False
    unit.save(update_fields=["is_active", "updated_at"])

    return unit


@transaction.atomic
def activate_unit(*, unit_id):
    """
    Reactivate a previously deactivated unit.
    """

    unit = Unit.objects.get(pk=unit_id)

    unit.is_active = True
    unit.save(update_fields=["is_active", "updated_at"])

    return unit


@transaction.atomic
def create_product(
    *,
    name,
    category_id,
    unit_id,
    current_purchase_cost,
    current_sell_price,
    minimum_stock,
):
    """
    Create a new product.

    Important:
    - New products start with zero stock.
    - Stock is introduced through the purchase workflow.
    - Category and unit must be active.
    """

    name = name.strip()

    if not name:
        raise ValidationError("Product name is required.")

    purchase_cost = Decimal(str(current_purchase_cost))
    sell_price = Decimal(str(current_sell_price))
    minimum_stock_level = Decimal(str(minimum_stock))

    if purchase_cost < 0:
        raise ValidationError(
            "Purchase cost cannot be negative."
        )

    if sell_price < 0:
        raise ValidationError(
            "Sell price cannot be negative."
        )

    if minimum_stock_level < 0:
        raise ValidationError(
            "Minimum stock cannot be negative."
        )

    category = Category.objects.get(pk=category_id)
    unit = Unit.objects.get(pk=unit_id)

    if not category.is_active:
        raise ValidationError(
            "Cannot assign an inactive category to a product."
        )

    if not unit.is_active:
        raise ValidationError(
            "Cannot assign an inactive unit to a product."
        )

    return Product.objects.create(
        name=name,
        category=category,
        unit=unit,
        current_purchase_cost=purchase_cost,
        current_sell_price=sell_price,
        minimum_stock=minimum_stock_level,
        current_stock=Decimal("0"),
        is_active=True,
    )


@transaction.atomic
def update_product(
    *,
    product_id,
    name,
    category_id,
    unit_id,
    current_purchase_cost,
    current_sell_price,
    minimum_stock,
):
    """
    Update product master data.

    Important:
    - Current purchase/sell prices can change.
    - Existing completed transactions keep their historical
      unit_price and unit_cost snapshots.
    - Current stock is NOT modified here.
    """

    product = (
        Product.objects
        .select_for_update()
        .get(pk=product_id)
    )

    name = name.strip()

    if not name:
        raise ValidationError("Product name is required.")

    purchase_cost = Decimal(str(current_purchase_cost))
    sell_price = Decimal(str(current_sell_price))
    minimum_stock_level = Decimal(str(minimum_stock))

    if purchase_cost < 0:
        raise ValidationError(
            "Purchase cost cannot be negative."
        )

    if sell_price < 0:
        raise ValidationError(
            "Sell price cannot be negative."
        )

    if minimum_stock_level < 0:
        raise ValidationError(
            "Minimum stock cannot be negative."
        )

    category = Category.objects.get(pk=category_id)
    unit = Unit.objects.get(pk=unit_id)

    if not category.is_active:
        raise ValidationError(
            "Cannot assign an inactive category to a product."
        )

    if not unit.is_active:
        raise ValidationError(
            "Cannot assign an inactive unit to a product."
        )

    product.name = name
    product.category = category
    product.unit = unit
    product.current_purchase_cost = purchase_cost
    product.current_sell_price = sell_price
    product.minimum_stock = minimum_stock_level

    product.save(
        update_fields=[
            "name",
            "category",
            "unit",
            "current_purchase_cost",
            "current_sell_price",
            "minimum_stock",
            "updated_at",
        ]
    )

    return product


@transaction.atomic
def deactivate_product(*, product_id):
    """
    Deactivate a product instead of deleting it.

    Historical transactions remain intact.
    """

    product = (
        Product.objects
        .select_for_update()
        .get(pk=product_id)
    )

    product.is_active = False
    product.save(update_fields=["is_active", "updated_at"])

    return product


@transaction.atomic
def activate_product(*, product_id):
    """
    Reactivate a previously deactivated product.
    """

    product = (
        Product.objects
        .select_for_update()
        .get(pk=product_id)
    )

    product.is_active = True
    product.save(update_fields=["is_active", "updated_at"])

    return product