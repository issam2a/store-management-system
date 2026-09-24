from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Expense

def generate_expense_reference():
    """
    Generate the next expense reference.

    Example:
    EXP-000001
    EXP-000002
    """

    last_expense = (
        Expense.objects
        .order_by("-id")
        .first()
    )

    if not last_expense:
        next_number = 1

    else:
        next_number = last_expense.id + 1

    return f"EXP-{next_number:06d}"


def record_expense(
    category,
    amount,
    payment_method,
    expense_date,
    created_by,
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

       

        expense = Expense.objects.create(
            reference=generate_expense_reference(),
            category=category.strip(),
            amount=amount,
            payment_method=payment_method.strip(),
            expense_date=expense_date,
            description=description.strip(),
            created_by=created_by,
        )

        return expense