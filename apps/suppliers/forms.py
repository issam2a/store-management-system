from django import forms

from .models import Supplier


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = [
            "name",
            "phone",
            "contact_information",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "autocomplete": "organization",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "autocomplete": "tel",
                }
            ),
            "contact_information": forms.Textarea(
                attrs={
                    "class": "form-input",
                    "rows": 4,
                }
            ),
        }

    def clean_name(self):
        name = self.cleaned_data["name"].strip()

        if not name:
            raise forms.ValidationError(
                "Supplier name is required."
            )

        return name

    def clean_phone(self):
        return self.cleaned_data["phone"].strip()

    def clean_contact_information(self):
        return self.cleaned_data[
            "contact_information"
        ].strip()