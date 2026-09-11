from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.products.models import Category, Product, Unit
from apps.suppliers.models import Supplier
from apps.purchases.models import Purchase, PurchaseItem
from apps.purchases.services import (
    add_purchase_item,
    cancel_purchase,
    complete_purchase,
    create_purchase,
    remove_purchase_item,
    update_purchase_item,
)
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


    def test_create_purchase_does_not_change_stock(self):
        from apps.purchases.services import create_purchase

        initial_stock = self.product.current_stock

        purchase = create_purchase(
            supplier=self.supplier,
            payment_type=Purchase.PaymentType.CASH,
            user=self.user,
        )

        self.product.refresh_from_db()

        self.assertEqual(
            purchase.status,
            Purchase.Status.DRAFT,
        )

        self.assertEqual(
            purchase.total_amount,
            Decimal("0.00"),
        )

        self.assertEqual(
            self.product.current_stock,
            initial_stock,
        )

    def test_adding_purchase_item_does_not_change_stock(self):
        from apps.purchases.services import add_purchase_item

        initial_stock = self.product.current_stock

        purchase = Purchase.objects.create(
            reference="PUR-TEST-003",
            supplier=self.supplier,
            payment_type=Purchase.PaymentType.CASH,
            created_by=self.user,
        )

        add_purchase_item(
            purchase_id=purchase.id,
            product=self.product,
            quantity=Decimal("3.000"),
            unit_cost=Decimal("1100.00"),
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.current_stock,
            initial_stock,
        )

        purchase.refresh_from_db()

        self.assertEqual(
            purchase.total_amount,
            Decimal("3300.00"),
        )

    def test_editing_purchase_item_does_not_change_stock(self):
        from apps.purchases.services import update_purchase_item

        initial_stock = self.product.current_stock

        item = self.purchase.items.first()

        update_purchase_item(
            item_id=item.id,
            quantity=Decimal("7.000"),
            unit_cost=Decimal("1300.00"),
        )

        self.product.refresh_from_db()
        self.purchase.refresh_from_db()
        item.refresh_from_db()

        self.assertEqual(
            self.product.current_stock,
            initial_stock,
        )

        self.assertEqual(
            item.quantity,
            Decimal("7.000"),
        )

        self.assertEqual(
            item.unit_cost,
            Decimal("1300.00"),
        )

        self.assertEqual(
            item.line_total,
            Decimal("9100.00"),
        )

        self.assertEqual(
            self.purchase.total_amount,
            Decimal("9100.00"),
        )

    def test_removing_purchase_item_does_not_change_stock(self):
        from apps.purchases.services import remove_purchase_item

        initial_stock = self.product.current_stock

        item = self.purchase.items.first()

        remove_purchase_item(item.id)

        self.product.refresh_from_db()
        self.purchase.refresh_from_db()

        self.assertEqual(
            self.product.current_stock,
            initial_stock,
        )

        self.assertFalse(
            PurchaseItem.objects.filter(
                id=item.id
            ).exists()
        )

        self.assertEqual(
            self.purchase.total_amount,
            Decimal("0.00"),
        )

    def test_completed_purchase_cannot_be_modified(self):
        from apps.purchases.services import (
            add_purchase_item,
            remove_purchase_item,
            update_purchase_item,
        )

        complete_purchase(
            purchase_id=self.purchase.id,
            user=self.user,
        )

        item = self.purchase.items.first()

        with self.assertRaises(ValidationError):
            add_purchase_item(
                purchase_id=self.purchase.id,
                product=self.product,
                quantity=Decimal("1.000"),
                unit_cost=Decimal("1000.00"),
            )

        with self.assertRaises(ValidationError):
            update_purchase_item(
                item_id=item.id,
                quantity=Decimal("2.000"),
                unit_cost=Decimal("1000.00"),
            )

        with self.assertRaises(ValidationError):
            remove_purchase_item(item.id)

    def test_draft_purchase_cannot_be_cancelled(self):
        with self.assertRaises(ValidationError):
            cancel_purchase(
                purchase_id=self.purchase.id,
                user=self.user,
                reason="Draft cancellation",
            )

    def test_cancellation_records_reason_user_and_timestamp(self):
        complete_purchase(
            purchase_id=self.purchase.id,
            user=self.user,
        )

        cancel_purchase(
            purchase_id=self.purchase.id,
            user=self.user,
            reason="Damaged goods received",
        )

        cancellation = TransactionCancellation.objects.get(
            purchase=self.purchase
        )

        self.purchase.refresh_from_db()

        self.assertEqual(
            cancellation.reason,
            "Damaged goods received",
        )

        self.assertEqual(
            cancellation.cancelled_by,
            self.user,
        )

        self.assertIsNotNone(
            self.purchase.cancelled_at
        )

        self.assertEqual(
            self.purchase.cancelled_by,
            self.user,
        )

    def test_cancellation_fails_when_stock_would_be_negative(self):
        complete_purchase(
            purchase_id=self.purchase.id,
            user=self.user,
        )

        # Simulate part of the purchased stock leaving inventory.
        self.product.refresh_from_db()

        self.product.current_stock = Decimal("4.000")
        self.product.save(
            update_fields=[
                "current_stock",
                "updated_at",
            ]
        )

        with self.assertRaises(ValidationError):
            cancel_purchase(
                purchase_id=self.purchase.id,
                user=self.user,
                reason="Supplier cancellation",
            )

        self.purchase.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(
            self.purchase.status,
            Purchase.Status.COMPLETED,
        )

        self.assertEqual(
            self.product.current_stock,
            Decimal("4.000"),
        )

        self.assertFalse(
            TransactionCancellation.objects.filter(
                purchase=self.purchase
            ).exists()
        )

    def test_cancellation_is_atomic(self):
        second_product = Product.objects.create(
            name="Second Test Product",
            category=self.category,
            unit=self.unit,
            current_purchase_cost=Decimal("500.00"),
            current_sell_price=Decimal("700.00"),
            minimum_stock=Decimal("5.000"),
            current_stock=Decimal("10.000"),
        )

        purchase = Purchase.objects.create(
            reference="PUR-TEST-004",
            supplier=self.supplier,
            payment_type=Purchase.PaymentType.CASH,
            created_by=self.user,
        )

        PurchaseItem.objects.create(
            purchase=purchase,
            product=self.product,
            quantity=Decimal("5.000"),
            unit_cost=Decimal("1200.00"),
            line_total=Decimal("6000.00"),
        )

        PurchaseItem.objects.create(
            purchase=purchase,
            product=second_product,
            quantity=Decimal("5.000"),
            unit_cost=Decimal("500.00"),
            line_total=Decimal("2500.00"),
        )

        complete_purchase(
            purchase_id=purchase.id,
            user=self.user,
        )

        self.product.refresh_from_db()
        second_product.refresh_from_db()

        self.assertEqual(
            self.product.current_stock,
            Decimal("15.000"),
        )

        self.assertEqual(
            second_product.current_stock,
            Decimal("15.000"),
        )

        # Simulate the second product no longer having enough stock
        # to reverse the purchase.
        second_product.current_stock = Decimal("4.000")
        second_product.save(
            update_fields=[
                "current_stock",
                "updated_at",
            ]
        )

        with self.assertRaises(ValidationError):
            cancel_purchase(
                purchase_id=purchase.id,
                user=self.user,
                reason="Atomicity test",
            )

        purchase.refresh_from_db()
        self.product.refresh_from_db()
        second_product.refresh_from_db()

        # The entire cancellation must be rolled back.
        self.assertEqual(
            purchase.status,
            Purchase.Status.COMPLETED,
        )

        self.assertEqual(
            self.product.current_stock,
            Decimal("15.000"),
        )

        self.assertEqual(
            second_product.current_stock,
            Decimal("4.000"),
        )

        self.assertFalse(
            TransactionCancellation.objects.filter(
                purchase=purchase
            ).exists()
        )
