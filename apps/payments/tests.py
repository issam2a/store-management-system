from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from apps.customers.models import Customer
from apps.products.models import Category, Product, Unit
from apps.sales.models import Sale, SaleItem

from .models import CustomerPayment
from .services import record_customer_payment


User = get_user_model()


class CustomerPaymentServiceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
        )

        self.category = Category.objects.create(
            name="Test Category",
        )

        self.unit = Unit.objects.create(
            name="Piece",
            symbol="pcs",
        )

        self.product = Product.objects.create(
            name="Product A",
            category=self.category,
            unit=self.unit,
            current_purchase_cost=Decimal("100.00"),
            current_sell_price=Decimal("150.00"),
            minimum_stock=Decimal("5.000"),
            current_stock=Decimal("100.000"),
        )

        self.customer = Customer.objects.create(
            name="Test Customer",
            phone="0999999999",
            
        )

    def create_credit_sale(
        self,
        amount=Decimal("1000.00"),
        reference="SALE-001",
    ):
        sale = Sale.objects.create(
            reference=reference,
            customer=self.customer,
            payment_type=Sale.PaymentType.CREDIT,
            status=Sale.Status.COMPLETED,
            subtotal_amount=amount,
            discount_amount=Decimal("0.00"),
            total_amount=amount,
            created_by=self.user,
            completed_by=self.user,
            completed_at=timezone.now(),
        )

        SaleItem.objects.create(
            sale=sale,
            product=self.product,
            quantity=Decimal("1.000"),
            unit_price=amount,
            line_total=amount,
        )

        return sale

    def create_customer_payment(
        self,
        amount=Decimal("100.00"),
        reference="PAY-001",
    ):
        return CustomerPayment.objects.create(
            reference=reference,
            customer=self.customer,
            amount=amount,
            payment_method="CASH",
            payment_date=date(2026, 9, 5),
            note="Test payment",
            recorded_by=self.user,
        )

    def record_payment(
        self,
        amount,
        reference="PAY-001",
        payment_method="Cash",
        payment_date=date(2026, 9, 5),
        note="",
    ):
        return record_customer_payment(
            customer_id=self.customer.id,
            amount=amount,
            payment_method=payment_method,
            payment_date=payment_date,
            reference=reference,
            recorded_by=self.user,
            note=note,
        )

    def test_record_customer_payment_successfully(self):
        self.create_credit_sale()

        payment = self.record_payment(
            amount=Decimal("300.00"),
        )

        self.assertEqual(
            payment.amount,
            Decimal("300.00"),
        )
        self.assertEqual(
            payment.customer,
            self.customer,
        )
        self.assertEqual(
            payment.recorded_by,
            self.user,
        )

    def test_partial_payment_reduces_outstanding_balance(self):
        self.create_credit_sale()

        self.record_payment(
            amount=Decimal("300.00"),
        )

        second_payment = self.record_payment(
            amount=Decimal("400.00"),
            reference="PAY-002",
        )

        self.assertEqual(
            second_payment.amount,
            Decimal("400.00"),
        )
        self.assertEqual(
            CustomerPayment.objects.filter(
                customer=self.customer,
            ).count(),
            2,
        )

    def test_exact_payment_is_allowed(self):
        self.create_credit_sale()

        payment = self.record_payment(
            amount=Decimal("1000.00"),
        )

        self.assertEqual(
            payment.amount,
            Decimal("1000.00"),
        )

    def test_overpayment_is_rejected(self):
        self.create_credit_sale()

        with self.assertRaises(ValidationError):
            self.record_payment(
                amount=Decimal("1000.01"),
            )

        self.assertEqual(
            CustomerPayment.objects.filter(
                customer=self.customer,
            ).count(),
            0,
        )

    def test_zero_payment_is_rejected(self):
        self.create_credit_sale()

        with self.assertRaises(ValidationError):
            self.record_payment(
                amount=Decimal("0.00"),
            )

        self.assertEqual(
            CustomerPayment.objects.filter(
                customer=self.customer,
            ).count(),
            0,
        )

    def test_negative_payment_is_rejected(self):
        self.create_credit_sale()

        with self.assertRaises(ValidationError):
            self.record_payment(
                amount=Decimal("-100.00"),
            )

        self.assertEqual(
            CustomerPayment.objects.filter(
                customer=self.customer,
            ).count(),
            0,
        )

    def test_payment_without_outstanding_balance_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.record_payment(
                amount=Decimal("100.00"),
            )

        self.assertEqual(
            CustomerPayment.objects.filter(
                customer=self.customer,
            ).count(),
            0,
        )

    def test_cash_sales_do_not_create_customer_balance(self):
        Sale.objects.create(
            reference="SALE-001",
            customer=self.customer,
            payment_type=Sale.PaymentType.CASH,
            status=Sale.Status.COMPLETED,
            subtotal_amount=Decimal("1000.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("1000.00"),
            created_by=self.user,
            completed_by=self.user,
            completed_at=timezone.now(),
        )

        with self.assertRaises(ValidationError):
            self.record_payment(
                amount=Decimal("100.00"),
            )

    def test_cancelled_credit_sales_do_not_create_customer_balance(self):
        Sale.objects.create(
            reference="SALE-001",
            customer=self.customer,
            payment_type=Sale.PaymentType.CREDIT,
            status=Sale.Status.CANCELLED,
            subtotal_amount=Decimal("1000.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("1000.00"),
            created_by=self.user,
            completed_by=self.user,
            completed_at=timezone.now(),
        )

        with self.assertRaises(ValidationError):
            self.record_payment(
                amount=Decimal("100.00"),
            )

    def test_previous_payments_are_subtracted_from_balance(self):
        self.create_credit_sale()

        self.create_customer_payment(
            amount=Decimal("600.00"),
            reference="PAY-001",
        )

        payment = self.record_payment(
            amount=Decimal("400.00"),
            reference="PAY-002",
        )

        self.assertEqual(
            payment.amount,
            Decimal("400.00"),
        )

    def test_payment_exceeding_remaining_balance_is_rejected(self):
        self.create_credit_sale()

        self.create_customer_payment(
            amount=Decimal("600.00"),
            reference="PAY-001",
        )

        with self.assertRaises(ValidationError):
            self.record_payment(
                amount=Decimal("400.01"),
                reference="PAY-002",
            )

        self.assertEqual(
            CustomerPayment.objects.filter(
                customer=self.customer,
            ).count(),
            1,
        )

    def test_payment_method_is_preserved(self):
        self.create_credit_sale()

        payment = self.record_payment(
            amount=Decimal("200.00"),
            payment_method="BANK_TRANSFER",
        )

        self.assertEqual(
            payment.payment_method,
            "BANK_TRANSFER",
        )

    def test_payment_date_is_preserved(self):
        self.create_credit_sale()

        payment = self.record_payment(
            amount=Decimal("200.00"),
            payment_date=date(2026, 8, 31),
        )

        self.assertEqual(
            payment.payment_date,
            date(2026, 8, 31),
        )

    def test_note_is_preserved(self):
        self.create_credit_sale()

        payment = self.record_payment(
            amount=Decimal("200.00"),
            note="Customer paid part of outstanding debt",
        )

        self.assertEqual(
            payment.note,
            "Customer paid part of outstanding debt",
        )

    def test_duplicate_reference_is_rejected(self):
        self.create_credit_sale()

        self.record_payment(
            amount=Decimal("200.00"),
            reference="PAY-001",
        )

        with self.assertRaises(IntegrityError):
            self.record_payment(
                amount=Decimal("100.00"),
                reference="PAY-001",
            )

        self.assertEqual(
            CustomerPayment.objects.filter(
                customer=self.customer,
            ).count(),
            1,
        )

