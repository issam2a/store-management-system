from django import forms

from .models import Category, Product, Unit


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "category",
            "unit",
            "current_purchase_cost",
            "current_sell_price",
            "minimum_stock",

        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Enter product name",
                }
            ),
            "category": forms.Select(),
            "unit": forms.Select(),
            "current_purchase_cost": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "current_sell_price": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "minimum_stock": forms.NumberInput(
                attrs={
                    "step": "0.001",
                    "min": "0",
                }
            ),
            
        }


    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["category"].queryset = Category.objects.filter(
            is_active=True
        )

        self.fields["unit"].queryset = Unit.objects.filter(
            is_active=True
        )

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Enter category name",
                }
            ),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "category",
            "unit",
            "current_purchase_cost",
            "current_sell_price",
            "minimum_stock",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "Enter product name"}
            ),
            "category": forms.Select(),
            "unit": forms.Select(),
            "current_purchase_cost": forms.NumberInput(
                attrs={"step": "0.01", "min": "0"}
            ),
            "current_sell_price": forms.NumberInput(
                attrs={"step": "0.01", "min": "0"}
            ),
            "minimum_stock": forms.NumberInput(
                attrs={"step": "0.001", "min": "0"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["category"].queryset = Category.objects.filter(
            is_active=True
        )

        self.fields["unit"].queryset = Unit.objects.filter(
            is_active=True
        )