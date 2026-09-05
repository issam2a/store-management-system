
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models, transaction

from apps.customers.models import Customer
from apps.purchases.models import Purchase
from apps.sales.models import Sale
from apps.suppliers.models import Supplier

from .models import CustomerPayment, SupplierPayment


def record_customer_payment(
    customer_id,
    amount,
    payment_method,
    payment_date,
    recorded_by,
    reference,
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

        # Validate payment amount
        if amount <= Decimal("0.00"):
            raise ValidationError(
                "Payment amount must be greater than zero."
            )

        # Validate payment method
        if not payment_method or not payment_method.strip():
            raise ValidationError(
                "Payment method is required."
            )

        # Validate payment date
        if not payment_date:
            raise ValidationError(
                "Payment date is required."
            )

        # Validate payment reference
        if not reference or not reference.strip():
            raise ValidationError(
                "Payment reference is required."
            )

        # Calculate total completed credit sales
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

        # Calculate previous customer payments
        previous_payments_total = (
            CustomerPayment.objects
            .filter(customer=customer)
            .aggregate(
                total=models.Sum("amount")
            )["total"]
            or Decimal("0.00")
        )

        # Calculate outstanding balance
        outstanding_balance = (
            credit_sales_total - previous_payments_total
        )

        # Prevent overpayment
        if amount > outstanding_balance:
            raise ValidationError(
                "Payment exceeds the customer's outstanding balance. "
                f"Outstanding: {outstanding_balance}, "
                f"payment: {amount}."
            )

        # Create payment
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


def record_supplier_payment(
    supplier_id,
    amount,
    payment_method,
    payment_date,
    recorded_by,
    reference,
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

        # Validate payment amount
        if amount <= Decimal("0.00"):
            raise ValidationError(
                "Payment amount must be greater than zero."
            )

        # Validate payment method
        if not payment_method or not payment_method.strip():
            raise ValidationError(
                "Payment method is required."
            )

        # Validate payment date
        if not payment_date:
            raise ValidationError(
                "Payment date is required."
            )

        # Validate payment reference
        if not reference or not reference.strip():
            raise ValidationError(
                "Payment reference is required."
            )

        # Calculate total completed credit purchases
        credit_purchases_total = (
            Purchase.objects
            .filter(
                supplier=supplier,
                payment_type=Purchase.PaymentType.CREDIT,
                status=Purchase.Status.COMPLETED,
            )
            .aggregate(
                total=models.Sum("total_amount")
            )["total"]
            or Decimal("0.00")
        )

        # Calculate previous supplier payments
        previous_payments_total = (
            SupplierPayment.objects
            .filter(supplier=supplier)
            .aggregate(
                total=models.Sum("amount")
            )["total"]
            or Decimal("0.00")
        )

        # Calculate outstanding balance
        outstanding_balance = (
            credit_purchases_total - previous_payments_total
        )

        # Prevent overpayment
        if amount > outstanding_balance:
            raise ValidationError(
                "Payment exceeds the supplier's outstanding balance. "
                f"Outstanding: {outstanding_balance}, "
                f"payment: {amount}."
            )

        # Create payment
        payment = SupplierPayment.objects.create(
            reference=reference.strip(),
            supplier=supplier,
            amount=amount,
            payment_method=payment_method.strip(),
            payment_date=payment_date,
            note=note.strip(),
            recorded_by=recorded_by,
        )

        return payment

