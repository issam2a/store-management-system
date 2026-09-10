from django import forms

from .models import Customer


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            "name",
            "phone",
            "contact_information",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "autocomplete": "name",
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
                "Customer name is required."
            )

        return name

    def clean_phone(self):
        return self.cleaned_data["phone"].strip()

    def clean_contact_information(self):
        return self.cleaned_data[
            "contact_information"
        ].strip()