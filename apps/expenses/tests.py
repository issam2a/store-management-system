
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from apps.expenses.models import Expense
from apps.expenses.services import record_expense

User = get_user_model()


class ExpenseServiceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
        )

    def record_valid_expense(
        self,
        reference="EXP-001",
        category="Utilities",
        amount=Decimal("100000.00"),
        payment_method="CASH",
        expense_date=date(2026, 9, 6),
        description="Test expense",
    ):
        return record_expense(
            category=category,
            amount=amount,
            payment_method=payment_method,
            expense_date=expense_date,
            created_by=self.user,
            reference=reference,
            description=description,
        )

    def test_record_expense_successfully(self):
        expense = self.record_valid_expense()

        self.assertEqual(
            Expense.objects.count(),
            1,
        )

        self.assertEqual(
            expense.amount,
            Decimal("100000.00"),
        )

        self.assertEqual(
            expense.category,
            "Utilities",
        )

    def test_zero_amount_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.record_valid_expense(
                amount=Decimal("0.00"),
            )

        self.assertEqual(
            Expense.objects.count(),
            0,
        )

    def test_negative_amount_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.record_valid_expense(
                amount=Decimal("-1.00"),
            )

        self.assertEqual(
            Expense.objects.count(),
            0,
        )

    def test_category_is_required(self):
        with self.assertRaises(ValidationError):
            self.record_valid_expense(
                category="",
            )

    def test_payment_method_is_required(self):
        with self.assertRaises(ValidationError):
            self.record_valid_expense(
                payment_method="",
            )

    def test_expense_date_is_required(self):
        with self.assertRaises(ValidationError):
            self.record_valid_expense(
                expense_date=None,
            )

    def test_reference_is_required(self):
        with self.assertRaises(ValidationError):
            self.record_valid_expense(
                reference="",
            )

    def test_description_is_preserved(self):
        expense = self.record_valid_expense(
            description="Electricity bill",
        )

        self.assertEqual(
            expense.description,
            "Electricity bill",
        )

    def test_duplicate_reference_is_rejected(self):
        self.record_valid_expense(
            reference="EXP-001",
        )

        with self.assertRaises(IntegrityError):
            self.record_valid_expense(
                reference="EXP-001",
            )

        self.assertEqual(
            Expense.objects.count(),
            1,
        )

    def test_transaction_rolls_back_on_failure(self):
        initial_count = Expense.objects.count()

        try:
            self.record_valid_expense(
                amount=Decimal("-100.00"),
            )
        except ValidationError:
            pass

        self.assertEqual(
            Expense.objects.count(),
            initial_count,
        )

