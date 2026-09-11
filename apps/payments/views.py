from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.customers.models import Customer

from .forms import CustomerPaymentForm
from .services import (
    get_customer_outstanding_balance,
    record_customer_payment,
)


@login_required
def customer_payment_create(request, customer_id):
    customer = get_object_or_404(
        Customer,
        pk=customer_id,
    )

    outstanding_balance = get_customer_outstanding_balance(
        customer.id
    )

    if request.method == "POST":
        form = CustomerPaymentForm(request.POST)

        if form.is_valid():
            try:
                record_customer_payment(
                    customer_id=customer.id,
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
                    "customer_detail",
                    customer_id=customer.id,
                )

    else:
        form = CustomerPaymentForm(
            initial={
                "payment_date": timezone.localdate(),
            }
        )

    return render(
        request,
        "customers/customer_payment_create.html",
        {
            "customer": customer,
            "outstanding_balance": outstanding_balance,
            "form": form,
        },
    )