from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.products.models import Category, Product, Unit
from apps.suppliers.models import Supplier
from apps.purchases.models import Purchase, PurchaseItem
from apps.purchases.services import complete_purchase, cancel_purchase
from apps.transactions.models import TransactionCancellation


User = get_user_model()


class PurchaseServiceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
        )

        self.category = Category.objects.create(
            name="Test Category"
        )

        self.unit = Unit.objects.create(
            name="Piece",
            symbol="pcs",
        )

        self.product = Product.objects.create(
            name="Test Product",
            category=self.category,
            unit=self.unit,
            current_purchase_cost=Decimal("1000.00"),
            current_sell_price=Decimal("1500.00"),
            minimum_stock=Decimal("5.000"),
            current_stock=Decimal("10.000"),
        )

        self.supplier = Supplier.objects.create(
            name="Test Supplier"
        )

        self.purchase = Purchase.objects.create(
            reference="PUR-TEST-001",
            supplier=self.supplier,
            payment_type=Purchase.PaymentType.CASH,
            created_by=self.user,
        )

        PurchaseItem.objects.create(
            purchase=self.purchase,
            product=self.product,
            quantity=Decimal("5.000"),
            unit_cost=Decimal("1200.00"),
            line_total=Decimal("0.00"),
        )

    def test_complete_purchase_updates_stock_and_total(self):
        complete_purchase(
            purchase_id=self.purchase.id,
            user=self.user,
        )

        self.purchase.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(
            self.purchase.status,
            Purchase.Status.COMPLETED,
        )

        self.assertEqual(
            self.purchase.total_amount,
            Decimal("6000.00"),
        )

        self.assertEqual(
            self.product.current_stock,
            Decimal("15.000"),
        )

        self.assertEqual(
            self.product.current_purchase_cost,
            Decimal("1200.00"),
        )

    def test_draft_purchase_cannot_be_completed_twice(self):
        complete_purchase(
            purchase_id=self.purchase.id,
            user=self.user,
        )

        with self.assertRaises(ValidationError):
            complete_purchase(
                purchase_id=self.purchase.id,
                user=self.user,
            )

    def test_purchase_cancellation_reverses_stock(self):
        complete_purchase(
            purchase_id=self.purchase.id,
            user=self.user,
        )

        cancel_purchase(
            purchase_id=self.purchase.id,
            user=self.user,
            reason="Supplier cancellation",
        )

        self.purchase.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(
            self.purchase.status,
            Purchase.Status.CANCELLED,
        )

        self.assertEqual(
            self.product.current_stock,
            Decimal("10.000"),
        )

        self.assertTrue(
            TransactionCancellation.objects.filter(
                purchase=self.purchase
            ).exists()
        )

    def test_purchase_cannot_be_cancelled_twice(self):
        complete_purchase(
            purchase_id=self.purchase.id,
            user=self.user,
        )

        cancel_purchase(
            purchase_id=self.purchase.id,
            user=self.user,
            reason="Supplier cancellation",
        )

        with self.assertRaises(ValidationError):
            cancel_purchase(
                purchase_id=self.purchase.id,
                user=self.user,
                reason="Second cancellation",
            )

    def test_cancellation_requires_reason(self):
        complete_purchase(
            purchase_id=self.purchase.id,
            user=self.user,
        )

        with self.assertRaises(ValidationError):
            cancel_purchase(
                purchase_id=self.purchase.id,
                user=self.user,
                reason="",
            )

    def test_draft_purchase_without_items_cannot_be_completed(self):
        empty_purchase = Purchase.objects.create(
            reference="PUR-TEST-002",
            supplier=self.supplier,
            payment_type=Purchase.PaymentType.CASH,
            created_by=self.user,
        )

        with self.assertRaises(ValidationError):
            complete_purchase(
                purchase_id=empty_purchase.id,
                user=self.user,
            )