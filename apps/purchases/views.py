from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from apps.products.services import create_product
from apps.transactions.models import TransactionCancellation

from .forms import (
    PurchaseForm,
    PurchaseItemForm,
    PurchaseProductForm,
    PurchaseCancellationForm,
)
from .models import Purchase, PurchaseItem
from .services import (
    create_purchase,
    add_purchase_item,
    update_purchase_item,
    remove_purchase_item,
    complete_purchase,
    delete_purchase,
    cancel_purchase,
)


@login_required
def purchase_list(request):
    query = request.GET.get("q", "").strip()
    selected_status = request.GET.get("status", "")

    purchases = (
        Purchase.objects
        .select_related(
            "supplier",
            "created_by",
        )
        .order_by("-created_at")
    )

    if query:
        purchases = purchases.filter(
            Q(reference__icontains=query)
            | Q(supplier__name__icontains=query)
        )

    if selected_status:
        purchases = purchases.filter(
            status=selected_status
        )

    paginator = Paginator(
        purchases,
        20,
    )

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(
        page_number
    )

    context = {
        "page_obj": page_obj,
        "paginator": paginator,
        "purchases": page_obj.object_list,
        "query": query,
        "selected_status": selected_status,
    }

    return render(
        request,
        "purchases/purchase_list.html",
        context,
    )


@login_required
def purchase_create(request):

    if request.method == "POST":

        form = PurchaseForm(
            request.POST
        )

        if form.is_valid():

            purchase = create_purchase(
                supplier=form.cleaned_data["supplier"],
                payment_type=form.cleaned_data["payment_type"],
                user=request.user,
            )

            messages.success(
                request,
                _("Purchase draft created successfully."),
            )

            return redirect(
                "purchase_detail",
                purchase.id,
            )

    else:
        form = PurchaseForm()

    context = {
        "form": form,
        "page_title": _("Create Purchase"),
        "submit_label": _("Create Draft"),
    }

    return render(
        request,
        "purchases/purchase_form.html",
        context,
    )


@login_required
def purchase_product_create(request, purchase_id):
    """
    Create a new product from a draft purchase workflow.

    The new product starts with zero stock.
    The actual purchase quantity and purchase cost are entered
    later as a PurchaseItem.
    """

    purchase = get_object_or_404(
        Purchase,
        pk=purchase_id,
    )

    if purchase.status != Purchase.Status.DRAFT:
        messages.error(
            request,
            _("Products can only be added while the purchase is a draft."),
        )

        return redirect(
            "purchase_detail",
            purchase.id,
        )

    if request.method == "POST":

        form = PurchaseProductForm(
            request.POST,
        )

        if form.is_valid():

            try:
                product = create_product(
                    name=form.cleaned_data["name"],
                    category_id=form.cleaned_data["category"].id,
                    unit_id=form.cleaned_data["unit"].id,
                    current_sell_price=form.cleaned_data["current_sell_price"],
                    minimum_stock=form.cleaned_data["minimum_stock"],
                )

            except ValidationError as error:

                form.add_error(
                    None,
                    error.message,
                )

            else:

                messages.success(
                    request,
                    _("Product created successfully."),
                )

                return redirect(
                    f"{reverse('purchase_item_create', args=[purchase.id])}"
                    f"?product={product.id}"
                )

    else:
        form = PurchaseProductForm()

    context = {
        "form": form,
        "purchase": purchase,
        "page_title": _("Create Product"),
        "submit_label": _("Create Product"),
    }

    return render(
        request,
        "purchases/purchase_product_form.html",
        context,
    )


@login_required
def purchase_item_create(request, purchase_id):
    purchase = get_object_or_404(
        Purchase,
        pk=purchase_id,
    )

    if purchase.status != Purchase.Status.DRAFT:
        messages.error(
            request,
            _("Items can only be added to draft purchases."),
        )

        return redirect(
            "purchase_detail",
            purchase.id,
        )

    selected_product_id = request.GET.get("product")

    if request.method == "POST":

        form = PurchaseItemForm(
            request.POST,
        )

        if form.is_valid():

            try:
                add_purchase_item(
                    purchase_id=purchase.id,
                    product=form.cleaned_data["product"],
                    quantity=form.cleaned_data["quantity"],
                    unit_cost=form.cleaned_data["unit_cost"],
                )

            except ValidationError as error:

                form.add_error(
                    None,
                    error.message,
                )

            else:

                messages.success(
                    request,
                    _("Purchase item added successfully."),
                )

                return redirect(
                    "purchase_detail",
                    purchase.id,
                )

    else:

        initial = {}

        if selected_product_id:
            initial["product"] = selected_product_id

        form = PurchaseItemForm(
            initial=initial,
        )

    context = {
        "form": form,
        "purchase": purchase,
        "page_title": _("Add Purchase Item"),
        "submit_label": _("Add Item"),
    }

    return render(
        request,
        "purchases/purchase_item_form.html",
        context,
    )


@login_required
def purchase_item_edit(request, item_id):
    item = get_object_or_404(
        PurchaseItem.objects.select_related(
            "purchase",
            "product",
        ),
        pk=item_id,
    )

    purchase = item.purchase

    if purchase.status != Purchase.Status.DRAFT:
        messages.error(
            request,
            _("Items can only be edited in draft purchases."),
        )

        return redirect(
            "purchase_detail",
            purchase.id,
        )

    if request.method == "POST":

        form = PurchaseItemForm(
            request.POST,
            instance=item,
        )

        if form.is_valid():

            try:
                update_purchase_item(
                    item_id=item.id,
                    quantity=form.cleaned_data["quantity"],
                    unit_cost=form.cleaned_data["unit_cost"],
                )

            except ValidationError as error:

                form.add_error(
                    None,
                    error.message,
                )

            else:

                messages.success(
                    request,
                    _("Purchase item updated successfully."),
                )

                return redirect(
                    "purchase_detail",
                    purchase.id,
                )

    else:
        form = PurchaseItemForm(
            instance=item,
        )

    context = {
        "form": form,
        "purchase": purchase,
        "item": item,
        "page_title": _("Edit Purchase Item"),
        "submit_label": _("Save Changes"),
    }

    return render(
        request,
        "purchases/purchase_item_form.html",
        context,
    )


@login_required
def purchase_detail(request, purchase_id):
    purchase = get_object_or_404(
        Purchase.objects.select_related(
            "supplier",
            "created_by",
            "completed_by",
            "cancelled_by",
        ),
        pk=purchase_id,
    )

    items = (
        purchase.items
        .select_related(
            "product",
            "product__unit",
        )
        .order_by("id")
    )

    cancellation = (
        TransactionCancellation.objects
        .select_related("cancelled_by")
        .filter(purchase=purchase)
        .first()
    )

    context = {
        "purchase": purchase,
        "items": items,
        "cancellation": cancellation,
    }

    return render(
        request,
        "purchases/purchase_detail.html",
        context,
    )


@login_required
@require_POST
def purchase_item_delete(request, item_id):
    item = get_object_or_404(
        PurchaseItem.objects.select_related("purchase"),
        pk=item_id,
    )

    purchase = item.purchase

    try:
        remove_purchase_item(item.id)

    except ValidationError as error:

        messages.error(
            request,
            error.message,
        )

    else:

        messages.success(
            request,
            _("Purchase item deleted successfully."),
        )

    return redirect(
        "purchase_detail",
        purchase.id,
    )


@login_required
@require_POST
def purchase_complete(request, purchase_id):
    purchase = get_object_or_404(
        Purchase,
        pk=purchase_id,
    )

    try:
        complete_purchase(
            purchase_id=purchase.id,
            user=request.user,
        )

    except ValidationError as error:

        messages.error(
            request,
            error.message,
        )

        return redirect(
            "purchase_detail",
            purchase.id,
        )

    messages.success(
        request,
        _("Purchase completed successfully."),
    )

    return redirect(
        "purchase_list"
    )


@login_required
@require_POST
def purchase_delete(request, purchase_id):
    purchase = get_object_or_404(
        Purchase,
        pk=purchase_id,
    )

    purchase_reference = purchase.reference

    try:
        delete_purchase(
            purchase.id
        )

    except ValidationError as error:

        messages.error(
            request,
            error.message,
        )

    else:

        messages.success(
            request,
            _("Purchase %(reference)s deleted successfully.")
            % {
                "reference": purchase_reference,
            },
        )

        return redirect(
            "purchase_list"
        )

    return redirect(
        "purchase_detail",
        purchase.id,
    )


@login_required
def purchase_cancel(request, purchase_id):
    purchase = get_object_or_404(
        Purchase,
        pk=purchase_id,
    )

    if purchase.status != Purchase.Status.COMPLETED:
        return redirect(
            "purchase_detail",
            purchase_id=purchase.id,
        )

    if request.method == "POST":

        form = PurchaseCancellationForm(
            request.POST
        )

        if form.is_valid():

            try:
                cancel_purchase(
                    purchase_id=purchase.id,
                    user=request.user,
                    reason=form.cleaned_data["reason"],
                )

            except ValidationError as exc:

                form.add_error(
                    None,
                    exc,
                )

            else:

                messages.success(
                    request,
                    _("Purchase cancelled successfully."),
                )

                return redirect(
                    "purchase_detail",
                    purchase_id=purchase.id,
                )

    else:
        form = PurchaseCancellationForm()

    return render(
        request,
        "purchases/purchase_cancel.html",
        {
            "purchase": purchase,
            "form": form,
        },
    )