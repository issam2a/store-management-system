from decimal import Decimal

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


INTEGER_UNITS = {
    "pc",
    "pcs",
    "piece",
    "pieces",
    "box",
    "boxes",
    "pack",
    "packs",
    "bag",
    "bags",
    "bottle",
    "bottles",
    "can",
    "cans",
}


def is_integer_unit(unit_symbol):
    return (
        str(unit_symbol).strip().lower()
        in INTEGER_UNITS
    )


def validate_quantity_for_unit(quantity, unit_symbol):
    """
    Validate a quantity according to the product's unit.

    Count-based units require whole numbers.
    Measurement-based units may contain decimals.
    """

    if quantity is None:
        return

    if quantity <= Decimal("0"):
        raise ValidationError(
            _("Quantity must be greater than zero.")
        )

    if is_integer_unit(unit_symbol):
        if quantity != quantity.to_integral_value():
            raise ValidationError(
                _(
                    "Quantity must be a whole number "
                    "for this unit."
                )
            )