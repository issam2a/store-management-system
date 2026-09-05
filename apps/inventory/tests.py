from decimal import Decimal
from django.db import IntegrityError


from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.products.models import Category, Product, Unit

from .models import InventoryAdjustment
from .services import apply_inventory_adjustment


User = get_user_model()


class InventoryAdjustmentServiceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
        )

        self.category = Category.objects.create(
            name="Test Category"
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

    def create_adjustment(
        self,
        adjustment_type,
        quantity=Decimal("1.000"),
        reason="Stock adjustment",
    ):
        return InventoryAdjustment.objects.create(
            reference="ADJ-001",
            product=self.product,
            adjustment_type=adjustment_type,
            quantity=quantity,
            reason=reason,
            created_by=self.user,
        )

    def test_increase_stock(self):
        adjustment = self.create_adjustment(
            InventoryAdjustment.AdjustmentType.INCREASE,
            quantity=Decimal("5.000"),
        )

        apply_inventory_adjustment(
            adjustment.id,
            self.user,
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.current_stock,
            Decimal("15.000"),
        )

    def test_decrease_stock(self):
        adjustment = self.create_adjustment(
            InventoryAdjustment.AdjustmentType.DECREASE,
            quantity=Decimal("4.000"),
        )

        apply_inventory_adjustment(
            adjustment.id,
            self.user,
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.current_stock,
            Decimal("6.000"),
        )

    def test_decrease_cannot_make_stock_negative(self):
        adjustment = self.create_adjustment(
            InventoryAdjustment.AdjustmentType.DECREASE,
            quantity=Decimal("11.000"),
        )

        with self.assertRaises(ValidationError):
            apply_inventory_adjustment(
                adjustment.id,
                self.user,
            )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.current_stock,
            Decimal("10.000"),
        )

    def test_zero_quantity_is_rejected_by_database(self):
        with self.assertRaises(Exception):
            self.create_adjustment(
                InventoryAdjustment.AdjustmentType.INCREASE,
                quantity=Decimal("0.000"),
            )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.current_stock,
            Decimal("10.000"),
        )


    def test_zero_quantity_is_rejected_by_database(self):
        with self.assertRaises(IntegrityError):
            self.create_adjustment(
                InventoryAdjustment.AdjustmentType.INCREASE,
                quantity=Decimal("0.000"),
            )


    def test_negative_quantity_is_rejected_by_database(self):
        with self.assertRaises(IntegrityError):
            self.create_adjustment(
                InventoryAdjustment.AdjustmentType.INCREASE,
                quantity=Decimal("-2.000"),
            )

    def test_reason_is_preserved(self):
        adjustment = self.create_adjustment(
            InventoryAdjustment.AdjustmentType.INCREASE,
            quantity=Decimal("3.000"),
            reason="Found additional stock",
        )

        apply_inventory_adjustment(
            adjustment.id,
            self.user,
        )

        adjustment.refresh_from_db()

        self.assertEqual(
            adjustment.reason,
            "Found additional stock",
        )

    def test_created_by_is_preserved(self):
        adjustment = self.create_adjustment(
            InventoryAdjustment.AdjustmentType.INCREASE,
            quantity=Decimal("2.000"),
        )

        apply_inventory_adjustment(
            adjustment.id,
            self.user,
        )

        adjustment.refresh_from_db()

        self.assertEqual(
            adjustment.created_by,
            self.user,
        )