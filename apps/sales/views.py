from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from apps.products.models import Product
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.core.paginator import Paginator

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

    paginator = Paginator(sales, 20)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    context = {
        "sales": page_obj,
        "page_obj": page_obj,
        "paginator": paginator,
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
        print(request.headers.get("X-Requested-With"))
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
    sale = get_object_or_404(
        Sale,
        pk=sale_id,
    )

    is_ajax = (
        request.headers.get(
            "X-Requested-With"
        ) == "XMLHttpRequest"
    )

    if request.method != "POST":

        if is_ajax:
            return JsonResponse(
                {
                    "success": False,
                    "error": "POST request required.",
                },
                status=400,
            )

        return redirect(
            "sale_detail",
            sale_id=sale.id,
        )

    form = SaleItemForm(request.POST)

    if form.is_valid():

        try:

            item = add_sale_item(
                sale_id=sale.id,
                product=form.cleaned_data["product"],
                quantity=form.cleaned_data.get(
                    "quantity"
                ),
                amount=form.cleaned_data.get(
                    "amount"
                ),
            )

        except ValidationError as exc:

            if is_ajax:
                return JsonResponse(
                    {
                        "success": False,
                        "error": str(exc),
                    },
                    status=400,
                )

            form.add_error(
                None,
                exc,
            )

        else:

            if is_ajax:

                sale.refresh_from_db()

                return JsonResponse(
                    {
                        "success": True,
                        "item": {
                            "id": item.id,
                            "product_id": item.product.id,
                            "product_name": item.product.name,
                            "quantity": str(item.quantity),
                            "unit": item.product.unit.symbol,
                            "unit_price": str(item.unit_price),
                            "line_total": str(item.line_total),
                            "update_url": reverse(
                            "sale_item_edit",
                            args=[item.id],
                        ),

                        "remove_url": reverse(
                            "sale_item_remove",
                            args=[item.id],
                        ),
                        },
                        "sale": {
                            "subtotal": str(
                                sale.subtotal_amount
                            ),
                            "total": str(
                                sale.total_amount
                            ),
                        },
                    }
                )

            return redirect(
                "sale_detail",
                sale_id=sale.id,
            )

    if is_ajax:

        return JsonResponse(
            {
                "success": False,
                "error": form.errors.as_text(),
            },
            status=400,
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
@require_POST
def sale_item_edit(request, item_id):
    item = get_object_or_404(
        SaleItem.objects.select_related(
            "sale",
            "product",
            "product__unit",
        ),
        pk=item_id,
    )

    sale = item.sale

    if sale.status != Sale.Status.DRAFT:
        return JsonResponse(
            {
                "success": False,
                "error": _("Only draft sales can be modified."),
            },
            status=400,
        )

    form = SaleItemUpdateForm(
        request.POST,
        product=item.product,
    )

    if not form.is_valid():
        return JsonResponse(
            {
                "success": False,
                "error": _("Enter a valid quantity."),
            },
            status=400,
        )

    try:
        item = update_sale_item(
            item_id=item.id,
            quantity=form.cleaned_data["quantity"],
        )

        sale.refresh_from_db()

    except ValidationError as exc:
        return JsonResponse(
            {
                "success": False,
                "error": exc.message,
            },
            status=400,
        )

    return JsonResponse(
        {
            "success": True,
            "item": {
                "id": item.id,
                "quantity": str(item.quantity),
                "line_total": str(item.line_total),
            },
            "sale": {
                "subtotal": str(sale.subtotal_amount),
                "total": str(sale.total_amount),
            },
        }
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