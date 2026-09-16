from django import forms

from apps.products.models import Product
from apps.suppliers.models import Supplier
from django.utils.translation import gettext_lazy as _
from .models import Purchase, PurchaseItem
from apps.products.quantity import validate_quantity_for_unit
from decimal import Decimal , ROUND_HALF_UP

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
                _("Supplier must be active.")
            )

        return supplier



class PurchaseItemForm(forms.ModelForm):
    package_quantity = forms.DecimalField(
        label=_("Package Quantity"),
        min_value=Decimal("0.001"),
        max_digits=14,
        decimal_places=3,
        widget=forms.NumberInput(
            attrs={
                "class": "form-input",
                "step": "0.001",
                "min": "0.001",
            }
        ),
    )

    units_per_package = forms.DecimalField(
        label=_("Units Per Package"),
        min_value=Decimal("0.001"),
        max_digits=14,
        decimal_places=3,
        widget=forms.NumberInput(
            attrs={
                "class": "form-input",
                "step": "0.001",
                "min": "0.001",
            }
        ),
    )

    package_cost = forms.DecimalField(
        label=_("Package Cost"),
        min_value=Decimal("0"),
        max_digits=14,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                "class": "form-input",
                "step": "0.01",
                "min": "0",
            }
        ),
    )

    class Meta:
        model = PurchaseItem
        fields = [
            "product",
            "quantity",
            "unit_cost",
        ]
        widgets = {
            "product": forms.Select(
                attrs={"class": "form-input"}
            ),
            "quantity": forms.HiddenInput(),
            "unit_cost": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["quantity"].required = False
        self.fields["unit_cost"].required = False

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
                _("Product must be active.")
            )

        return product

    def clean(self):
        cleaned_data = super().clean()

        package_quantity = cleaned_data.get("package_quantity")
        units_per_package = cleaned_data.get("units_per_package")
        package_cost = cleaned_data.get("package_cost")
        product = cleaned_data.get("product")

        if (
            package_quantity is None
            or units_per_package is None
            or package_cost is None
            or product is None
        ):
            return cleaned_data

        quantity = (
            package_quantity * units_per_package
        )

        unit_cost = (
            package_cost / units_per_package
        ).quantize(
            Decimal("0.000001"),
            rounding=ROUND_HALF_UP,
        )

        validate_quantity_for_unit(
            quantity,
            product.unit.symbol,
        )

        cleaned_data["quantity"] = quantity
        cleaned_data["unit_cost"] = unit_cost

        return cleaned_data

        return cleaned_data
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
            "quantity": forms.HiddenInput(),
            "unit_cost": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["quantity"].required = False
        self.fields["unit_cost"].required = False

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
                _("Product must be active.")
            )

        return product


    

PurchaseItemFormSet = forms.inlineformset_factory(
    Purchase,
    PurchaseItem,
    form=PurchaseItemForm,
    extra=1,
    can_delete=True,
)

class PurchaseProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "category",
            "unit",
            "current_sell_price",
            "minimum_stock",
        ]

        labels = {
            "name": _("Product Name"),
            "category": _("Category"),
            "unit": _("Unit"),
            "current_sell_price": _("Selling Price"),
            "minimum_stock": _("Minimum Stock"),
        }

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "autocomplete": "off",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "form-input",
                }
            ),
            "unit": forms.Select(
                attrs={
                    "class": "form-input",
                }
            ),
            "current_sell_price": forms.NumberInput(
                attrs={
                    "class": "form-input",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "minimum_stock": forms.NumberInput(
                attrs={
                    "class": "form-input",
                    "step": "0.001",
                    "min": "0",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["category"].queryset = (
            self.fields["category"].queryset
            .filter(is_active=True)
            .order_by("name")
        )

        self.fields["unit"].queryset = (
            self.fields["unit"].queryset
            .filter(is_active=True)
            .order_by("name")
        )

    def clean_name(self):
        name = self.cleaned_data["name"].strip()

        if not name:
            raise forms.ValidationError(
                _("Product name is required.")
            )

        return name

    def clean_current_sell_price(self):
        price = self.cleaned_data["current_sell_price"]

        if price < 0:
            raise forms.ValidationError(
                _("Selling price cannot be negative.")
            )

        return price

    def clean_minimum_stock(self):
        minimum_stock = self.cleaned_data["minimum_stock"]

        if minimum_stock < 0:
            raise forms.ValidationError(
                _("Minimum stock cannot be negative.")
            )

        return minimum_stock

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