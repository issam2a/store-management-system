from decimal import Decimal

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Expense



EXPENSE_CATEGORY_CHOICES = [
    ("rent", _("Rent")),
    ("electricity", _("Electricity")),
    ("water", _("Water")),
    ("internet", _("Internet")),
    ("transport", _("Transport")),
    ("maintenance", _("Maintenance")),
    ("salary", _("Salary")),
    ("tax", _("Tax")),
    ("supplies", _("Supplies")),
    ("other", _("Other")),
]


PAYMENT_METHOD_CHOICES = [
    ("cash", _("Cash")),
    ("card", _("Card")),
    ("bank", _("Bank Transfer")),
]
class ExpenseForm(forms.Form):
    

    category = forms.ChoiceField(
        label=_("Category"),
        choices=EXPENSE_CATEGORY_CHOICES,
        widget=forms.Select(
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

    payment_method = forms.ChoiceField(
        label=_("Payment Method"),
        choices=PAYMENT_METHOD_CHOICES,
        widget=forms.Select(
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

    

    def clean_category(self):
        return self.cleaned_data["category"]


      
    def clean_payment_method(self):
        return self.cleaned_data["payment_method"]