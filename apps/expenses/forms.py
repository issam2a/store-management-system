from decimal import Decimal

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Expense


class ExpenseForm(forms.Form):
    reference = forms.CharField(
        label=_("Reference"),
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
            }
        ),
    )

    category = forms.CharField(
        label=_("Category"),
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
            }
        ),
    )

    amount = forms.DecimalField(
        label=_("Amount"),
        max_digits=14,
        decimal_places=2,
        min_value=Decimal("0.01"),
        widget=forms.NumberInput(
            attrs={
                "class": "form-input",
                "step": "0.01",
                "min": "0.01",
            }
        ),
    )

    payment_method = forms.CharField(
        label=_("Payment Method"),
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
            }
        ),
    )

    expense_date = forms.DateField(
        label=_("Expense Date"),
        widget=forms.DateInput(
            attrs={
                "class": "form-input",
                "type": "date",
            }
        ),
    )

    description = forms.CharField(
        label=_("Description"),
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-input",
                "rows": 4,
            }
        ),
    )

    def clean_reference(self):
        reference = (
            self.cleaned_data["reference"]
            .strip()
        )

        if Expense.objects.filter(
            reference=reference
        ).exists():
            raise forms.ValidationError(
                _("An expense with this reference already exists.")
            )

        return reference

    def clean_category(self):
        category = (
            self.cleaned_data["category"]
            .strip()
        )

        if not category:
            raise forms.ValidationError(
                _("Category is required.")
            )

        return category

    def clean_payment_method(self):
        payment_method = (
            self.cleaned_data["payment_method"]
            .strip()
        )

        if not payment_method:
            raise forms.ValidationError(
                _("Payment method is required.")
            )

        return payment_method