from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Expense


def record_expense(
    category,
    amount,
    payment_method,
    expense_date,
    created_by,
    reference,
    description="",
):
    """
    Record a business expense.
    """

    with transaction.atomic():

        amount = Decimal(amount)

        if amount <= Decimal("0.00"):
            raise ValidationError(
                "Expense amount must be greater than zero."
            )

        if not category or not category.strip():
            raise ValidationError(
                "Expense category is required."
            )

        if not payment_method or not payment_method.strip():
            raise ValidationError(
                "Payment method is required."
            )

        if not expense_date:
            raise ValidationError(
                "Expense date is required."
            )

        if not reference or not reference.strip():
            raise ValidationError(
                "Expense reference is required."
            )

        expense = Expense.objects.create(
            reference=reference.strip(),
            category=category.strip(),
            amount=amount,
            payment_method=payment_method.strip(),
            expense_date=expense_date,
            description=description.strip(),
            created_by=created_by,
        )

        return expense