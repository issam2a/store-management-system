from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import F, Q
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from apps.products.models import Product

from .forms import InventoryAdjustmentForm
from .models import InventoryAdjustment
from .services import apply_inventory_adjustment


@login_required
def inventory_list(request):
    """
    Display current inventory with search and stock-status filtering.
    """

    query = request.GET.get("q", "").strip()
    selected_status = request.GET.get("status", "").strip()

    products = (
        Product.objects
        .select_related("category", "unit")
        .filter(is_active=True)
        .order_by("name")
    )

    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(category__name__icontains=query)
        )

    if selected_status == "LOW":
        products = products.filter(
            current_stock__gt=0,
            current_stock__lte=F("minimum_stock"),
        )

    elif selected_status == "OUT":
        products = products.filter(
            current_stock=0,
        )

    elif selected_status == "HEALTHY":
        products = products.filter(
            current_stock__gt=F("minimum_stock"),
        )

    context = {
        "products": products,
        "query": query,
        "selected_status": selected_status,
    }

    return render(
        request,
        "inventory/inventory_list.html",
        context,
    )


@login_required
def inventory_adjustment_create(request):
    """
    Create and immediately apply an inventory adjustment.
    """

    if request.method == "POST":
        form = InventoryAdjustmentForm(request.POST)

        if form.is_valid():
            adjustment = form.save(commit=False)

            adjustment.reference = generate_inventory_reference()
            adjustment.created_by = request.user
            adjustment.save()

            try:
                apply_inventory_adjustment(
                    adjustment_id=adjustment.id,
                    user=request.user,
                )
            except ValidationError as exc:
                adjustment.delete()
                form.add_error(None, exc)
            else:
                messages.success(
                    request,
                    _("Inventory adjustment applied successfully."),
                )
                return redirect("inventory_list")

    else:
        form = InventoryAdjustmentForm()

    products = (
        Product.objects
        .filter(is_active=True)
        .select_related("unit")
        .order_by("name")
    )

    product_stock_data = {
        str(product.id): {
            "stock": float(product.current_stock),
            "unit": product.unit.symbol,
        }
        for product in products
    }

    return render(
        request,
        "inventory/inventory_adjustment_form.html",
        {
            "form": form,
            "page_title": _("Inventory Adjustment"),
            "submit_label": _("Apply Adjustment"),
            "product_stock_data": product_stock_data,
        },
    )


@login_required
def inventory_adjustment_history(request):
    """
    Display historical inventory adjustments.
    """

    adjustments = (
        InventoryAdjustment.objects
        .select_related(
            "product",
            "product__unit",
            "product__category",
            "created_by",
            "applied_by",
        )
        .filter(applied_at__isnull=False)
        .order_by("-applied_at")
    )

    return render(
        request,
        "inventory/inventory_adjustment_history.html",
        {
            "adjustments": adjustments,
        },
    )


def generate_inventory_reference():
    last_adjustment = (
        InventoryAdjustment.objects
        .order_by("-id")
        .first()
    )

    next_number = (
        last_adjustment.id + 1
        if last_adjustment
        else 1
    )

    return f"ADJ-{next_number:06d}"