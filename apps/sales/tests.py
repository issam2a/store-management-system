
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.customers.models import Customer
from apps.products.models import Category, Product, Unit
from apps.transactions.models import TransactionCancellation

from .models import Sale, SaleItem
from .services import complete_sale, cancel_sale


User = get_user_model()


class SalesServiceTests(TestCase):
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
            current_stock=Decimal("10.000"),
        )

        self.product_b = Product.objects.create(
            name="Product B",
            category=self.category,
            unit=self.unit,
            current_purchase_cost=Decimal("200.00"),
            current_sell_price=Decimal("300.00"),
            minimum_stock=Decimal("5.000"),
            current_stock=Decimal("20.000"),
        )

        self.customer = Customer.objects.create(
            name="Test Customer",
            phone="0999999999",
            account_status="ACTIVE",
        )

    def create_sale(
        self,
        payment_type=Sale.PaymentType.CASH,
        customer=None,
        reference="SALE-001",
        discount=Decimal("0.00"),
    ):
        return Sale.objects.create(
            reference=reference,
            customer=customer,
            payment_type=payment_type,
            discount_amount=discount,
            created_by=self.user,
        )

    def add_item(
        self,
        sale,
        product=None,
        quantity=Decimal("1.000"),
        unit_price=None,
    ):
        product = product or self.product

        if unit_price is None:
            unit_price = product.current_sell_price

        return SaleItem.objects.create(
            sale=sale,
            product=product,
            quantity=quantity,
            unit_price=unit_price,
            line_total=Decimal("0.00"),
        )

    def test_successful_sale_completion(self):
        sale = self.create_sale()

        self.add_item(
            sale,
            quantity=Decimal("2.000"),
            unit_price=Decimal("150.00"),
        )

        completed_sale = complete_sale(
            sale.id,
            self.user,
        )

        completed_sale.refresh_from_db()

        self.assertEqual(
            completed_sale.status,
            Sale.Status.COMPLETED,
        )
        self.assertIsNotNone(completed_sale.completed_at)
        self.assertEqual(
            completed_sale.completed_by,
            self.user,
        )

    def test_multiple_sale_items(self):
        sale = self.create_sale()

        item_a = self.add_item(
            sale,
            product=self.product,
            quantity=Decimal("2.000"),
            unit_price=Decimal("150.00"),
        )

        item_b = self.add_item(
            sale,
            product=self.product_b,
            quantity=Decimal("3.000"),
            unit_price=Decimal("300.00"),
        )

        complete_sale(sale.id, self.user)

        sale.refresh_from_db()
        item_a.refresh_from_db()
        item_b.refresh_from_db()

        self.assertEqual(
            sale.subtotal_amount,
            Decimal("1200.00"),
        )

        self.assertEqual(
            item_a.line_total,
            Decimal("300.00"),
        )

        self.assertEqual(
            item_b.line_total,
            Decimal("900.00"),
        )

    def test_stock_reduction(self):
        sale = self.create_sale()

        self.add_item(
            sale,
            quantity=Decimal("3.000"),
            unit_price=Decimal("150.00"),
        )

        complete_sale(sale.id, self.user)

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.current_stock,
            Decimal("7.000"),
        )

    def test_insufficient_stock(self):
        sale = self.create_sale()

        self.add_item(
            sale,
            quantity=Decimal("11.000"),
            unit_price=Decimal("150.00"),
        )

        with self.assertRaises(ValidationError):
            complete_sale(sale.id, self.user)

        sale.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(
            sale.status,
            Sale.Status.DRAFT,
        )

        self.assertEqual(
            self.product.current_stock,
            Decimal("10.000"),
        )

    def test_subtotal_calculation(self):
        sale = self.create_sale()

        self.add_item(
            sale,
            product=self.product,
            quantity=Decimal("2.000"),
            unit_price=Decimal("150.00"),
        )

        self.add_item(
            sale,
            product=self.product_b,
            quantity=Decimal("4.000"),
            unit_price=Decimal("300.00"),
        )

        complete_sale(sale.id, self.user)

        sale.refresh_from_db()

        self.assertEqual(
            sale.subtotal_amount,
            Decimal("1500.00"),
        )

        self.assertEqual(
            sale.total_amount,
            Decimal("1500.00"),
        )


    def test_discount_calculation(self):
        sale = self.create_sale()

        # The database requires discount_amount <= subtotal_amount
        # and total_amount = subtotal_amount - discount_amount.
        sale.subtotal_amount = Decimal("3000.00")
        sale.discount_amount = Decimal("500.00")
        sale.total_amount = Decimal("2500.00")
        sale.save(
            update_fields=[
                "subtotal_amount",
                "discount_amount",
                "total_amount",
            ]
        )

        self.add_item(
            sale,
            quantity=Decimal("10.000"),
            unit_price=Decimal("300.00"),
        )

        complete_sale(sale.id, self.user)

        sale.refresh_from_db()

        self.assertEqual(
            sale.subtotal_amount,
            Decimal("3000.00"),
        )

        self.assertEqual(
            sale.discount_amount,
            Decimal("500.00"),
        )

        self.assertEqual(
            sale.total_amount,
            Decimal("2500.00"),
        )

    def test_cash_sale(self):
        sale = self.create_sale(
            payment_type=Sale.PaymentType.CASH,
            customer=None,
        )

        self.add_item(
            sale,
            quantity=Decimal("2.000"),
            unit_price=Decimal("150.00"),
        )

        complete_sale(sale.id, self.user)

        sale.refresh_from_db()

        self.assertEqual(
            sale.payment_type,
            Sale.PaymentType.CASH,
        )

        self.assertIsNone(sale.customer)

        self.assertEqual(
            sale.status,
            Sale.Status.COMPLETED,
        )

    def test_credit_sale_with_customer(self):
        sale = self.create_sale(
            payment_type=Sale.PaymentType.CREDIT,
            customer=self.customer,
        )

        self.add_item(
            sale,
            quantity=Decimal("2.000"),
            unit_price=Decimal("150.00"),
        )

        complete_sale(sale.id, self.user)

        sale.refresh_from_db()

        self.assertEqual(
            sale.payment_type,
            Sale.PaymentType.CREDIT,
        )

        self.assertEqual(
            sale.customer,
            self.customer,
        )

        self.assertEqual(
            sale.status,
            Sale.Status.COMPLETED,
        )

    def test_credit_sale_without_customer(self):
        sale = self.create_sale(
            payment_type=Sale.PaymentType.CREDIT,
            customer=None,
        )

        self.add_item(
            sale,
            quantity=Decimal("1.000"),
            unit_price=Decimal("150.00"),
        )

        with self.assertRaises(ValidationError):
            complete_sale(sale.id, self.user)

        sale.refresh_from_db()

        self.assertEqual(
            sale.status,
            Sale.Status.DRAFT,
        )

    def test_empty_sale(self):
        sale = self.create_sale()

        with self.assertRaises(ValidationError):
            complete_sale(sale.id, self.user)

        sale.refresh_from_db()

        self.assertEqual(
            sale.status,
            Sale.Status.DRAFT,
        )

    def test_duplicate_completion(self):
        sale = self.create_sale()

        self.add_item(
            sale,
            quantity=Decimal("2.000"),
            unit_price=Decimal("150.00"),
        )

        complete_sale(sale.id, self.user)

        with self.assertRaises(ValidationError):
            complete_sale(sale.id, self.user)

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.current_stock,
            Decimal("8.000"),
        )

    def test_cancellation(self):
        sale = self.create_sale()

        self.add_item(
            sale,
            quantity=Decimal("3.000"),
            unit_price=Decimal("150.00"),
        )

        complete_sale(sale.id, self.user)

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.current_stock,
            Decimal("7.000"),
        )

        cancelled_sale, cancellation = cancel_sale(
            sale.id,
            self.user,
            "Customer cancelled the order.",
        )

        cancelled_sale.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(
            cancelled_sale.status,
            Sale.Status.CANCELLED,
        )

        self.assertIsNotNone(
            cancelled_sale.cancelled_at,
        )

        self.assertEqual(
            cancelled_sale.cancelled_by,
            self.user,
        )

        self.assertEqual(
            self.product.current_stock,
            Decimal("10.000"),
        )

        self.assertEqual(
            cancellation.reason,
            "Customer cancelled the order.",
        )

        self.assertTrue(
            TransactionCancellation.objects.filter(
                sale=sale,
            ).exists()
        )

    def test_duplicate_cancellation(self):
        sale = self.create_sale()

        self.add_item(
            sale,
            quantity=Decimal("2.000"),
            unit_price=Decimal("150.00"),
        )

        complete_sale(sale.id, self.user)

        cancel_sale(
            sale.id,
            self.user,
            "First cancellation.",
        )

        with self.assertRaises(ValidationError):
            cancel_sale(
                sale.id,
                self.user,
                "Second cancellation.",
            )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.current_stock,
            Decimal("10.000"),
        )

        self.assertEqual(
            TransactionCancellation.objects.filter(
                sale=sale,
            ).count(),
            1,
        )

    def test_cancellation_reason_required(self):
        sale = self.create_sale()

        self.add_item(
            sale,
            quantity=Decimal("2.000"),
            unit_price=Decimal("150.00"),
        )

        complete_sale(sale.id, self.user)

        with self.assertRaises(ValidationError):
            cancel_sale(
                sale.id,
                self.user,
                "",
            )

        with self.assertRaises(ValidationError):
            cancel_sale(
                sale.id,
                self.user,
                "   ",
            )

        sale.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(
            sale.status,
            Sale.Status.COMPLETED,
        )

        self.assertEqual(
            self.product.current_stock,
            Decimal("8.000"),
        )

        self.assertFalse(
            TransactionCancellation.objects.filter(
                sale=sale,
            ).exists()
        )

    def test_completion_rollback_when_one_item_has_insufficient_stock(self):
        sale = self.create_sale()

        # First item is valid and would normally reduce stock.
        self.add_item(
            sale,
            product=self.product,
            quantity=Decimal("3.000"),
            unit_price=Decimal("150.00"),
        )

        # Second item exceeds available stock.
        self.add_item(
            sale,
            product=self.product_b,
            quantity=Decimal("21.000"),
            unit_price=Decimal("300.00"),
        )

        with self.assertRaises(ValidationError):
            complete_sale(sale.id, self.user)

        sale.refresh_from_db()
        self.product.refresh_from_db()
        self.product_b.refresh_from_db()

        # Transaction must roll back completely.
        self.assertEqual(
            sale.status,
            Sale.Status.DRAFT,
        )

        self.assertEqual(
            sale.subtotal_amount,
            Decimal("0.00"),
        )

        self.assertEqual(
            sale.total_amount,
            Decimal("0.00"),
        )

        self.assertEqual(
            self.product.current_stock,
            Decimal("10.000"),
        )

        self.assertEqual(
            self.product_b.current_stock,
            Decimal("20.000"),
        )

