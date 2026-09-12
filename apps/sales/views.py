from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from apps.products.models import Product

from .forms import (
    SaleCancellationForm,
    SaleCreateForm,
    SaleDiscountForm,
    SaleItemForm,
    SaleItemUpdateForm,
)
from .models import Sale, SaleItem
from .services import (
    add_sale_item,
    cancel_sale,
    complete_sale,
    create_sale,
    remove_sale_item,
    set_sale_discount,
    update_sale_item,
)


@login_required
def sale_list(request):
    """
    Display sales history with search and status filtering.

    Search:
    - Sale reference
    - Customer name

    Filters:
    - Draft
    - Completed
    - Cancelled
    """

    query = request.GET.get("q", "").strip()
    selected_status = request.GET.get("status", "").strip()

    sales = (
        Sale.objects
        .select_related(
            "customer",
            "created_by",
            "completed_by",
        )
        .order_by("-created_at")
    )

    if query:
        sales = sales.filter(
            Q(reference__icontains=query)
            | Q(customer__name__icontains=query)
        )

    if selected_status:
        sales = sales.filter(
            status=selected_status
        )

    context = {
        "sales": sales,
        "query": query,
        "selected_status": selected_status,
    }

    return render(
        request,
        "sales/sale_list.html",
        context,
    )


@login_required
def sale_create(request):
    """
    Start a new draft sale.
    """

    if request.method == "POST":
        form = SaleCreateForm(request.POST)

        if form.is_valid():
            try:
                sale = create_sale(
                    customer=form.cleaned_data["customer"],
                    payment_type=form.cleaned_data["payment_type"],
                    user=request.user,
                )

            except ValidationError as exc:
                form.add_error(
                    None,
                    exc,
                )

            else:
                return redirect(
                    "sale_detail",
                    sale_id=sale.id,
                )

    else:
        form = SaleCreateForm(
            initial={
                "payment_type": Sale.PaymentType.CASH,
            }
        )

    context = {
        "form": form,
    }

    return render(
        request,
        "sales/sale_create.html",
        context,
    )


@login_required
def sale_detail(request, sale_id):
    """
    Main POS workspace.

    The sale detail page becomes the cashier's working screen.

    It displays:
    - Sale information
    - Customer
    - Payment type
    - Current cart
    - Totals
    - Product selection form
    - Discount form
    - Completion controls
    """

    sale = get_object_or_404(
        Sale.objects.select_related(
            "customer",
            "created_by",
            "completed_by",
            "cancelled_by",
        ),
        pk=sale_id,
    )

    items = (
        sale.items
        .select_related(
            "product",
            "product__unit",
        )
        .order_by("id")
    )

    context = {
        "sale": sale,
        "items": items,
        "item_form": SaleItemForm(),
        "discount_form": SaleDiscountForm(
            initial={
                "discount_amount": sale.discount_amount,
            }
        ),
        "cancellation_form": SaleCancellationForm(),
    }

    return render(
        request,
        "sales/sale_detail.html",
        context,
    )


@login_required
def sale_item_create(request, sale_id):
    """
    Add a product to the POS cart.

    The product selling price is determined by the service
    from Product.current_sell_price.
    """

    sale = get_object_or_404(
        Sale,
        pk=sale_id,
    )

    if request.method != "POST":
        return redirect(
            "sale_detail",
            sale_id=sale.id,
        )

    form = SaleItemForm(request.POST)

    if form.is_valid():
        try:
            add_sale_item(
                sale_id=sale.id,
                product=form.cleaned_data["product"],
                quantity=form.cleaned_data.get("quantity"),
                amount=form.cleaned_data.get("amount"),
            )

        except ValidationError as exc:
            form.add_error(
                None,
                exc,
            )

        else:
            return redirect(
                "sale_detail",
                sale_id=sale.id,
            )

    items = (
        sale.items
        .select_related(
            "product",
            "product__unit",
        )
        .order_by("id")
    )

    context = {
        "sale": sale,
        "items": items,
        "item_form": form,
        "discount_form": SaleDiscountForm(
            initial={
                "discount_amount": sale.discount_amount,
            }
        ),
        "cancellation_form": SaleCancellationForm(),
    }

    return render(
        request,
        "sales/sale_detail.html",
        context,
    )


@login_required
def sale_item_edit(request, item_id):
    """
    Update the quantity of an existing cart item.

    This is an auxiliary endpoint for the POS interface.
    """

    item = get_object_or_404(
        SaleItem.objects.select_related(
            "sale",
            "product",
        ),
        pk=item_id,
    )

    sale = item.sale

    if request.method != "POST":
        return redirect(
            "sale_detail",
            sale_id=sale.id,
        )

    form = SaleItemUpdateForm(request.POST)

    if form.is_valid():
        try:
            update_sale_item(
                item_id=item.id,
                quantity=form.cleaned_data["quantity"],
            )

        except ValidationError as exc:
            form.add_error(
                None,
                exc,
            )

        else:
            return redirect(
                "sale_detail",
                sale_id=sale.id,
            )

    items = (
        sale.items
        .select_related(
            "product",
            "product__unit",
        )
        .order_by("id")
    )

    context = {
        "sale": sale,
        "items": items,
        "item_form": SaleItemForm(),
        "discount_form": SaleDiscountForm(
            initial={
                "discount_amount": sale.discount_amount,
            }
        ),
        "cancellation_form": SaleCancellationForm(),
        "item_update_form": form,
        "editing_item": item,
    }

    return render(
        request,
        "sales/sale_detail.html",
        context,
    )


@login_required
def sale_item_remove(request, item_id):
    """
    Remove an item from the POS cart.
    """

    item = get_object_or_404(
        SaleItem.objects.select_related("sale"),
        pk=item_id,
    )

    sale = item.sale

    if request.method != "POST":
        return redirect(
            "sale_detail",
            sale_id=sale.id,
        )

    try:
        remove_sale_item(
            item.id,
        )

    except ValidationError:
        return redirect(
            "sale_detail",
            sale_id=sale.id,
        )

    return redirect(
        "sale_detail",
        sale_id=sale.id,
    )


@login_required
def sale_discount_update(request, sale_id):
    """
    Update the discount on the current draft sale.
    """

    sale = get_object_or_404(
        Sale,
        pk=sale_id,
    )

    if request.method != "POST":
        return redirect(
            "sale_detail",
            sale_id=sale.id,
        )

    form = SaleDiscountForm(request.POST)

    if form.is_valid():
        try:
            set_sale_discount(
                sale_id=sale.id,
                discount_amount=form.cleaned_data[
                    "discount_amount"
                ],
            )

        except ValidationError as exc:
            form.add_error(
                None,
                exc,
            )

        else:
            return redirect(
                "sale_detail",
                sale_id=sale.id,
            )

    items = (
        sale.items
        .select_related(
            "product",
            "product__unit",
        )
        .order_by("id")
    )

    context = {
        "sale": sale,
        "items": items,
        "item_form": SaleItemForm(),
        "discount_form": form,
        "cancellation_form": SaleCancellationForm(),
    }

    return render(
        request,
        "sales/sale_detail.html",
        context,
    )


@login_required
def sale_complete(request, sale_id):
    """
    Complete the current POS sale.
    """

    sale = get_object_or_404(
        Sale,
        pk=sale_id,
    )

    if request.method != "POST":
        return redirect(
            "sale_detail",
            sale_id=sale.id,
        )

    try:
        complete_sale(
            sale_id=sale.id,
            user=request.user,
        )

    except ValidationError as exc:
        items = (
            sale.items
            .select_related(
                "product",
                "product__unit",
            )
            .order_by("id")
        )

        context = {
            "sale": sale,
            "items": items,
            "item_form": SaleItemForm(),
            "discount_form": SaleDiscountForm(
                initial={
                    "discount_amount": sale.discount_amount,
                }
            ),
            "cancellation_form": SaleCancellationForm(),
            "completion_error": exc,
        }

        return render(
            request,
            "sales/sale_detail.html",
            context,
        )

    return redirect(
        "sale_detail",
        sale_id=sale.id,
    )


@login_required
def sale_cancel(request, sale_id):
    """
    Cancel a completed sale.
    """

    sale = get_object_or_404(
        Sale,
        pk=sale_id,
    )

    if request.method != "POST":
        return redirect(
            "sale_detail",
            sale_id=sale.id,
        )

    form = SaleCancellationForm(request.POST)

    if form.is_valid():
        try:
            cancel_sale(
                sale_id=sale.id,
                user=request.user,
                reason=form.cleaned_data["reason"],
            )

        except ValidationError as exc:
            form.add_error(
                None,
                exc,
            )

        else:
            return redirect(
                "sale_detail",
                sale_id=sale.id,
            )

    items = (
        sale.items
        .select_related(
            "product",
            "product__unit",
        )
        .order_by("id")
    )

    context = {
        "sale": sale,
        "items": items,
        "item_form": SaleItemForm(),
        "discount_form": SaleDiscountForm(
            initial={
                "discount_amount": sale.discount_amount,
            }
        ),
        "cancellation_form": form,
        "cancellation_error": None,
    }

    return render(
        request,
        "sales/sale_detail.html",
        context,
    )


@login_required
def product_search(request):
    """
    Search active products for the POS interface.

    Expected query parameter:

        ?q=chocolate

    Returns JSON containing:
    - product id
    - name
    - unit
    - available stock
    - current selling price
    """

    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse(
            {
                "results": [],
            }
        )

    products = (
        Product.objects
        .filter(
            is_active=True,
            name__icontains=query,
        )
        .select_related("unit")
        .order_by("name")[:20]
    )

    results = []

    for product in products:
        results.append(
            {
                "id": product.id,
                "name": product.name,
                "unit": product.unit.symbol,
                "stock": str(product.current_stock),
                "price": str(
                    product.current_sell_price
                ),
            }
        )

    return JsonResponse(
        {
            "results": results,
        }
    )