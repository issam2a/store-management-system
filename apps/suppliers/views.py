from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import SupplierForm
from .models import Supplier
from .services import (
    activate_supplier,
    create_supplier,
    deactivate_supplier,
    update_supplier,
)
from apps.payments.forms import SupplierPaymentForm
from apps.payments.services import (
    get_supplier_outstanding_balance,
    record_supplier_payment,
)

def supplier_list(request):
    suppliers = Supplier.objects.all()

    query = request.GET.get("q", "").strip()
    selected_status = request.GET.get("status", "").strip()

    if query:
        suppliers = suppliers.filter(
            Q(name__icontains=query)
            | Q(phone__icontains=query)
            | Q(contact_information__icontains=query)
        )

    if selected_status == "active":
        suppliers = suppliers.filter(
            is_active=True,
        )

    elif selected_status == "inactive":
        suppliers = suppliers.filter(
            is_active=False,
        )

    suppliers = suppliers.order_by("name")

    paginator = Paginator(
        suppliers,
        10,
    )

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(
        page_number,
    )

    return render(
        request,
        "suppliers/supplier_list.html",
        {
            "suppliers": page_obj,
            "page_obj": page_obj,
            "paginator": paginator,
            "query": query,
            "selected_status": selected_status,
        },
    )


def supplier_create(request):
    if request.method == "POST":
        form = SupplierForm(request.POST)

        if form.is_valid():
            try:
                create_supplier(
                    name=form.cleaned_data["name"],
                    phone=form.cleaned_data["phone"],
                    contact_information=form.cleaned_data[
                        "contact_information"
                    ],
                )
            except ValidationError as exc:
                form.add_error(None, exc)
            else:
                messages.success(
                    request,
                    _("Supplier created successfully."),
                )
                
                next_url = request.GET.get("next") or request.POST.get("next")

                if next_url:
                    return redirect(next_url)
                return redirect("supplier_list")

    else:
        form = SupplierForm()

    return render(
        request,
        "suppliers/supplier_form.html",
        {
            "form": form,
            "page_title": _("Create Supplier"),
            "page_description": _(
                "Add a new supplier to your store."
            ),
            "submit_label": _("Create Supplier"),
            "is_edit": False,
        },
    )


def supplier_edit(request, supplier_id):
    supplier = get_object_or_404(
        Supplier,
        pk=supplier_id,
    )

    if request.method == "POST":
        form = SupplierForm(request.POST)

        if form.is_valid():
            try:
                update_supplier(
                    supplier_id=supplier.id,
                    name=form.cleaned_data["name"],
                    phone=form.cleaned_data["phone"],
                    contact_information=form.cleaned_data[
                        "contact_information"
                    ],
                )
            except ValidationError as exc:
                form.add_error(None, exc)
            else:
                messages.success(
                    request,
                    _("Supplier updated successfully."),
                )

                return redirect("supplier_list")

    else:
        form = SupplierForm(
            initial={
                "name": supplier.name,
                "phone": supplier.phone,
                "contact_information": (
                    supplier.contact_information
                ),
            }
        )

    return render(
        request,
        "suppliers/supplier_form.html",
        {
            "form": form,
            "supplier": supplier,
            "page_title": _("Edit Supplier"),
            "page_description": _(
                "Update supplier information."
            ),
            "submit_label": _("Save Changes"),
            "is_edit": True,
        },
    )


def supplier_activate(request, supplier_id):
    if request.method == "POST":
        try:
            activate_supplier(
                supplier_id=supplier_id,
            )
        except ValidationError as exc:
            messages.error(
                request,
                str(exc),
            )
        else:
            messages.success(
                request,
                _("Supplier activated successfully."),
            )

    return redirect("supplier_list")


def supplier_deactivate(request, supplier_id):
    if request.method == "POST":
        try:
            deactivate_supplier(
                supplier_id=supplier_id,
            )
        except ValidationError as exc:
            messages.error(
                request,
                str(exc),
            )
        else:
            messages.success(
                request,
                _("Supplier deactivated successfully."),
            )

    return redirect("supplier_list")

@login_required
def supplier_detail(request, supplier_id):
    supplier = get_object_or_404(
        Supplier,
        pk=supplier_id,
    )

    outstanding_balance = get_supplier_outstanding_balance(
        supplier.id
    )

    purchases = (
        supplier.purchases
        .select_related("created_by")
        .order_by("-created_at")
    )

    payments = (
        supplier.payments
        .select_related("recorded_by")
        .order_by("-payment_date", "-created_at")
    )

    context = {
        "supplier": supplier,
        "outstanding_balance": outstanding_balance,
        "purchases": purchases,
        "payments": payments,
    }

    return render(
        request,
        "suppliers/supplier_detail.html",
        context,
    )

@login_required
def supplier_payment_create(request, supplier_id):
    supplier = get_object_or_404(
        Supplier,
        pk=supplier_id,
    )

    outstanding_balance = get_supplier_outstanding_balance(
        supplier.id
    )

    if request.method == "POST":
        form = SupplierPaymentForm(request.POST)

        if form.is_valid():
            try:
                record_supplier_payment(
                    supplier_id=supplier.id,
                    amount=form.cleaned_data["amount"],
                    payment_method=form.cleaned_data["payment_method"],
                    payment_date=form.cleaned_data["payment_date"],
                    recorded_by=request.user,
                    note=form.cleaned_data["note"],
                )

            except ValidationError as exc:
                form.add_error(None, exc)

            else:
                return redirect(
                    "supplier_detail",
                    supplier_id=supplier.id,
                )

    else:
        form = SupplierPaymentForm(
            initial={
                "payment_date": timezone.localdate(),
            }
        )

    return render(
        request,
        "suppliers/supplier_payment_create.html",
        {
            "supplier": supplier,
            "outstanding_balance": outstanding_balance,
            "form": form,
        },
    )