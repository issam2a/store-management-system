from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models, transaction

from apps.customers.models import Customer
from apps.purchases.models import Purchase
from apps.sales.models import Sale
from apps.suppliers.models import Supplier

from .models import CustomerPayment, SupplierPayment


def generate_customer_payment_reference():
    last_payment = CustomerPayment.objects.order_by("-id").first()

    if last_payment is None:
        next_number = 1
    else:
        next_number = last_payment.id + 1

    return f"CUS-PAY-{next_number:06d}"


def generate_supplier_payment_reference():
    last_payment = SupplierPayment.objects.order_by("-id").first()

    if last_payment is None:
        next_number = 1
    else:
        next_number = last_payment.id + 1

    return f"SUP-PAY-{next_number:06d}"


def record_customer_payment(
    customer_id,
    amount,
    payment_method,
    payment_date,
    recorded_by,
    note="",
):
    """
    Record a customer payment against outstanding credit sales.
    """

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
            reference=generate_customer_payment_reference(),
            customer=customer,
            amount=amount,
            payment_method=payment_method.strip(),
            payment_date=payment_date,
            note=note.strip(),
            recorded_by=recorded_by,
        )

        return payment


def get_supplier_outstanding_balance(supplier_id):
    """
    Calculate the supplier's outstanding balance.

    Balance:
        completed credit purchases
        minus supplier payments
    """

    credit_purchases_total = (
        Purchase.objects
        .filter(
            supplier_id=supplier_id,
            payment_type=Purchase.PaymentType.CREDIT,
            status=Purchase.Status.COMPLETED,
        )
        .aggregate(
            total=models.Sum("total_amount")
        )["total"]
        or Decimal("0.00")
    )

    supplier_payments_total = (
        SupplierPayment.objects
        .filter(
            supplier_id=supplier_id,
        )
        .aggregate(
            total=models.Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    return (
        credit_purchases_total - supplier_payments_total
    ).quantize(Decimal("0.01"))


def record_supplier_payment(
    supplier_id,
    amount,
    payment_method,
    payment_date,
    recorded_by,
    note="",
):
    """
    Record a supplier payment against outstanding credit purchases.
    """

    with transaction.atomic():
        supplier = (
            Supplier.objects
            .select_for_update()
            .get(pk=supplier_id)
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

        outstanding_balance = get_supplier_outstanding_balance(
            supplier.id
        )

        if amount > outstanding_balance:
            raise ValidationError(
                "Payment exceeds the supplier's outstanding balance. "
                f"Outstanding: {outstanding_balance}, "
                f"payment: {amount}."
            )

        payment = SupplierPayment.objects.create(
            reference=generate_supplier_payment_reference(),
            supplier=supplier,
            amount=amount,
            payment_method=payment_method.strip(),
            payment_date=payment_date,
            note=note.strip(),
            recorded_by=recorded_by,
        )

        return payment