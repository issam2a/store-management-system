from django import forms
from django.utils.translation import gettext_lazy as _


class SupplierPaymentForm(forms.Form):
    amount = forms.DecimalField(
        label=_("Amount"),
        min_value=0.01,
        max_digits=14,
        decimal_places=2,
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
                "autocomplete": "off",
            }
        ),
    )

    payment_date = forms.DateField(
        label=_("Payment Date"),
        widget=forms.DateInput(
            attrs={
                "class": "form-input",
                "type": "date",
            }
        ),
    )

    note = forms.CharField(
        label=_("Note"),
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-input",
                "rows": 4,
            }
        ),
    )

    def clean_payment_method(self):
        payment_method = self.cleaned_data["payment_method"].strip()

        if not payment_method:
            raise forms.ValidationError(
                _("Payment method is required.")
            )

        return payment_method

    def clean_note(self):
        return self.cleaned_data["note"].strip()