from decimal import Decimal

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.customers.models import Customer
from apps.products.models import Product

from .models import Sale

class SaleCreateForm(forms.Form):
    """
    Form for starting a new POS sale.

    Business logic remains in the sales service.
    """

    customer = forms.ModelChoiceField(
        label=_("Customer"),
        queryset=(
            Customer.objects
            .filter(is_active=True)
            .order_by("name")
        ),
        required=False,
        empty_label=_("Walk-in Customer"),
        widget=forms.Select(
            attrs={
                "class": "form-input",
            }
        ),
    )

    payment_type = forms.ChoiceField(
        label=_("Payment Type"),
        choices=Sale.PaymentType.choices,
        initial=Sale.PaymentType.CASH,
        widget=forms.Select(
            attrs={
                "class": "form-input",
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()

        customer = cleaned_data.get("customer")
        payment_type = cleaned_data.get("payment_type")

        if (
            payment_type == Sale.PaymentType.CREDIT
            and customer is None
        ):
            raise forms.ValidationError(
                _("A credit sale requires a customer.")
            )

        return cleaned_data


class SaleItemForm(forms.Form):
    product = forms.ModelChoiceField(
        label=_("Product"),
        queryset=(
            Product.objects
            .filter(is_active=True)
            .select_related("unit")
            .order_by("name")
        ),
        empty_label=None,
        widget=forms.Select(
            attrs={
                "class": "form-input",
            }
        ),
    )

    quantity = forms.DecimalField(
        label=_("Quantity"),
        max_digits=14,
        decimal_places=3,
        min_value=Decimal("0.001"),
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-input",
                "step": "0.001",
                "min": "0.001",
            }
        ),
    )

    amount = forms.DecimalField(
        label=_("Amount"),
        max_digits=14,
        decimal_places=2,
        min_value=Decimal("0.01"),
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-input",
                "step": "0.01",
                "min": "0.01",
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()

        quantity = cleaned_data.get("quantity")
        amount = cleaned_data.get("amount")

        if quantity is None and amount is None:
            raise forms.ValidationError(
                _("Enter a quantity or an amount.")
            )

        if quantity is not None and quantity <= 0:
            raise forms.ValidationError(
                _("Quantity must be greater than zero.")
            )

        if amount is not None and amount <= 0:
            raise forms.ValidationError(
                _("Amount must be greater than zero.")
            )

        return cleaned_data

class SaleItemUpdateForm(forms.Form):
    """
    Form used when changing the quantity of an existing
    product already present in the POS cart.
    """

    quantity = forms.DecimalField(
        label=_("Quantity"),
        max_digits=14,
        decimal_places=3,
        min_value=Decimal("0.001"),
        widget=forms.NumberInput(
            attrs={
                "class": "form-input",
                "step": "0.001",
                "min": "0.001",
            }
        ),
    )

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]

        if quantity <= 0:
            raise forms.ValidationError(
                _("Quantity must be greater than zero.")
            )

        return quantity


class SaleDiscountForm(forms.Form):
    """
    Form for changing the discount on a draft sale.
    """

    discount_amount = forms.DecimalField(
        label=_("Discount"),
        max_digits=14,
        decimal_places=2,
        min_value=0,
        required=False,
        initial=0,
        widget=forms.NumberInput(
            attrs={
                "class": "form-input",
                "step": "0.01",
                "min": "0",
            }
        ),
    )

    def clean_discount_amount(self):
        discount_amount = (
            self.cleaned_data["discount_amount"]
            or Decimal("0.00")
        )

        if discount_amount < 0:
            raise forms.ValidationError(
                _("Discount cannot be negative.")
            )

        return discount_amount


class SaleCancellationForm(forms.Form):
    """
    Form for cancelling a completed sale.
    """

    reason = forms.CharField(
        label=_("Cancellation Reason"),
        required=True,
        widget=forms.Textarea(
            attrs={
                "class": "form-input",
                "rows": 4,
                "required": True,
            }
        ),
    )

    def clean_reason(self):
        reason = self.cleaned_data["reason"].strip()

        if not reason:
            raise forms.ValidationError(
                _("A cancellation reason is required.")
            )

        return reason