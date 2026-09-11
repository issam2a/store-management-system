from django import forms

from apps.products.models import Product
from apps.suppliers.models import Supplier
from django.utils.translation import gettext_lazy as _
from .models import Purchase, PurchaseItem


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = [
            "supplier",
            "payment_type",
        ]

        widgets = {
            "supplier": forms.Select(
                attrs={
                    "class": "form-input",
                }
            ),
            "payment_type": forms.Select(
                attrs={
                    "class": "form-input",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["supplier"].queryset = (
            Supplier.objects
            .filter(is_active=True)
            .order_by("name")
        )

    def clean_supplier(self):
        supplier = self.cleaned_data["supplier"]

        if not supplier.is_active:
            raise forms.ValidationError(
                "Supplier must be active."
            )

        return supplier


class PurchaseItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseItem
        fields = [
            "product",
            "quantity",
            "unit_cost",
        ]

        widgets = {
            "product": forms.Select(
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
            "unit_cost": forms.NumberInput(
                attrs={
                    "class": "form-input",
                    "step": "0.01",
                    "min": "0",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["product"].queryset = (
            Product.objects
            .filter(is_active=True)
            .select_related("unit", "category")
            .order_by("name")
        )

    def clean_product(self):
        product = self.cleaned_data["product"]

        if not product.is_active:
            raise forms.ValidationError(
                "Product must be active."
            )

        return product

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]

        if quantity <= 0:
            raise forms.ValidationError(
                "Quantity must be greater than zero."
            )

        return quantity

    def clean_unit_cost(self):
        unit_cost = self.cleaned_data["unit_cost"]

        if unit_cost < 0:
            raise forms.ValidationError(
                "Unit cost cannot be negative."
            )

        return unit_cost

PurchaseItemFormSet = forms.inlineformset_factory(
    Purchase,
    PurchaseItem,
    form=PurchaseItemForm,
    extra=1,
    can_delete=True,
)


class PurchaseCancellationForm(forms.Form):
    reason = forms.CharField(
        label=_("Cancellation Reason"),
        widget=forms.Textarea(
            attrs={
                "class": "form-input",
                "rows": 4,
            }
        ),
        required=True,
    )

    def clean_reason(self):
        reason = self.cleaned_data["reason"].strip()

        if not reason:
            raise forms.ValidationError(
                _("Cancellation reason is required.")
            )

        return reason