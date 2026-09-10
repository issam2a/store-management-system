from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from .forms import CustomerForm
from .models import Customer
from .services import (
    activate_customer,
    create_customer,
    deactivate_customer,
    update_customer,
)


def customer_list(request):
    customers = Customer.objects.all()

    query = request.GET.get("q", "").strip()
    selected_status = request.GET.get("status", "").strip()

    if query:
        customers = customers.filter(
            Q(name__icontains=query)
            | Q(phone__icontains=query)
            | Q(contact_information__icontains=query)
        )

    if selected_status == "active":
        customers = customers.filter(is_active=True)

    elif selected_status == "inactive":
        customers = customers.filter(is_active=False)

    customers = customers.order_by("name")

    paginator = Paginator(
        customers,
        10,
    )

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(
        page_number,
    )

    return render(
        request,
        "customers/customer_list.html",
        {
            "customers": page_obj,
            "page_obj": page_obj,
            "paginator": paginator,
            "query": query,
            "selected_status": selected_status,
        },
    )


def customer_create(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)

        if form.is_valid():
            try:
                create_customer(
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
                    _("Customer created successfully."),
                )

                return redirect("customer_list")

    else:
        form = CustomerForm()

    return render(
        request,
        "customers/customer_form.html",
        {
            "form": form,
            "page_title": _("Create Customer"),
            "page_description": _(
                "Add a new customer to your store."
            ),
            "submit_label": _("Create Customer"),
            "is_edit": False,
        },
    )


def customer_edit(request, customer_id):
    customer = get_object_or_404(
        Customer,
        pk=customer_id,
    )

    if request.method == "POST":
        form = CustomerForm(request.POST)

        if form.is_valid():
            try:
                update_customer(
                    customer_id=customer.id,
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
                    _("Customer updated successfully."),
                )

                return redirect("customer_list")

    else:
        form = CustomerForm(
            initial={
                "name": customer.name,
                "phone": customer.phone,
                "contact_information": customer.contact_information,
            }
        )

    return render(
        request,
        "customers/customer_form.html",
        {
            "form": form,
            "customer": customer,
            "page_title": _("Edit Customer"),
            "page_description": _(
                "Update customer information."
            ),
            "submit_label": _("Save Changes"),
            "is_edit": True,
        },
    )


def customer_activate(request, customer_id):
    if request.method == "POST":
        try:
            activate_customer(
                customer_id=customer_id,
            )
        except ValidationError as exc:
            messages.error(
                request,
                str(exc),
            )
        else:
            messages.success(
                request,
                _("Customer activated successfully."),
            )

    return redirect("customer_list")


def customer_deactivate(request, customer_id):
    if request.method == "POST":
        try:
            deactivate_customer(
                customer_id=customer_id,
            )
        except ValidationError as exc:
            messages.error(
                request,
                str(exc),
            )
        else:
            messages.success(
                request,
                _("Customer deactivated successfully."),
            )

    return redirect("customer_list")