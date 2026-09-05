from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models, transaction

from apps.customers.models import Customer
from apps.sales.models import Sale

from .models import CustomerPayment


def record_customer_payment(
    customer_id,
    amount,
    payment_method,
    payment_date,
    recorded_by,
    reference,
    note="",
):
    with transaction.atomic():
        customer = (
            Customer.objects
            .select_for_update()
            .get(pk=customer_id)
        )

        amount = Decimal(amount)

        if amount <= Decimal("0.00"):
            raise ValidationError(
                "Payment amount must be greater than zero."
            )

        if not payment_method or not payment_method.strip():
            raise ValidationError(
                "Payment method is required."
            )

        if not payment_date:
            raise ValidationError(
                "Payment date is required."
            )

        if not reference or not reference.strip():
            raise ValidationError(
                "Payment reference is required."
            )

        credit_sales_total = (
            Sale.objects
            .filter(
                customer=customer,
                payment_type=Sale.PaymentType.CREDIT,
                status=Sale.Status.COMPLETED,
            )
            .aggregate(
                total=models.Sum("total_amount")
            )["total"]
            or Decimal("0.00")
        )

        previous_payments_total = (
            CustomerPayment.objects
            .filter(customer=customer)
            .aggregate(
                total=models.Sum("amount")
            )["total"]
            or Decimal("0.00")
        )

        outstanding_balance = (
            credit_sales_total - previous_payments_total
        )

        if amount > outstanding_balance:
            raise ValidationError(
                "Payment exceeds the customer's outstanding balance. "
                f"Outstanding: {outstanding_balance}, "
                f"payment: {amount}."
            )

        payment = CustomerPayment.objects.create(
            reference=reference.strip(),
            customer=customer,
            amount=amount,
            payment_method=payment_method.strip(),
            payment_date=payment_date,
            note=note.strip(),
            recorded_by=recorded_by,
        )

        return payment