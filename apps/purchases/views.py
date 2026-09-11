from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
    
)

from .forms import PurchaseForm, PurchaseItemForm ,PurchaseCancellationForm
from .models import Purchase ,PurchaseItem
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
                "Purchase draft created successfully."
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


def purchase_item_create(request, purchase_id):
    purchase = get_object_or_404(
        Purchase,
        pk=purchase_id,
    )

    if purchase.status != Purchase.Status.DRAFT:
        messages.error(
            request,
            "Items can only be added to draft purchases.",
        )
        return redirect(
            "purchase_detail",
            purchase.id,
        )

    if request.method == "POST":

        form = PurchaseItemForm(
            request.POST
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
                    "Purchase item added successfully.",
                )

                return redirect(
                    "purchase_detail",
                    purchase.id,
                )

    else:
        form = PurchaseItemForm()

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
            "Items can only be edited in draft purchases.",
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
                    "Purchase item updated successfully.",
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


def purchase_detail(request, purchase_id):
    purchase = get_object_or_404(
        Purchase.objects.select_related(
            "supplier",
            "created_by",
            "completed_by",
            "cancelled_by",
        ).prefetch_related(
            "items__product",
        ),
        pk=purchase_id,
    )

    context = {
        "purchase": purchase,
        "items": purchase.items.all(),
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
            "Purchase item deleted successfully.",
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
        "Purchase completed successfully.",
    )

    return redirect("purchase_list")
@login_required
@require_POST
def purchase_delete(request, purchase_id):
    purchase = get_object_or_404(
        Purchase,
        pk=purchase_id,
    )

    purchase_reference = purchase.reference

    try:
        delete_purchase(purchase.id)

    except ValidationError as error:
        messages.error(
            request,
            error.message,
        )

    else:
        messages.success(
            request,
            f"Purchase {purchase_reference} deleted successfully.",
        )

        return redirect("purchase_list")

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
        form = PurchaseCancellationForm(request.POST)

        if form.is_valid():
            try:
                cancel_purchase(
                    purchase_id=purchase.id,
                    user=request.user,
                    reason=form.cleaned_data["reason"],
                )

            except ValidationError as exc:
                form.add_error(None, exc)

            else:
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