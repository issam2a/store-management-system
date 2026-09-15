from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.products.models import Product

from .models import InventoryAdjustment
from apps.products.quantity import validate_quantity_for_unit

class InventoryAdjustmentForm(forms.ModelForm):
    class Meta:
        model = InventoryAdjustment
        fields = [
            "product",
            "adjustment_type",
            "quantity",
            "reason",
        ]
        labels = {
            "product": _("Product"),
            "adjustment_type": _("Adjustment"),
            "quantity": _("Quantity"),
            "reason": _("Reason"),
        }
        widgets = {
            "product": forms.Select(
                attrs={
                    "class": "form-input",
                }
            ),
            "adjustment_type": forms.Select(
                attrs={
                    "class": "form-input",
                }
            ),
            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-input",
                    "step": "0.001",
                    "min": "0.001",
                }
            ),
            "reason": forms.Textarea(
                attrs={
                    "class": "form-input",
                    "rows": 4,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["product"].queryset = (
            Product.objects
            .filter(is_active=True)
            .select_related("category", "unit")
            .order_by("name")
        )

    def clean_product(self):
        product = self.cleaned_data["product"]

        if not product.is_active:
            raise ValidationError(
                _("Product must be active.")
            )

        return product

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]

        product = self.cleaned_data.get("product")

        if not product:
            return quantity

        validate_quantity_for_unit(
            quantity,
            product.unit.symbol,
        )

        return quantity

    def clean_reason(self):
        reason = self.cleaned_data["reason"].strip()

        if not reason:
            raise ValidationError(
                _("A reason is required for an inventory adjustment.")
            )

        return reason


    