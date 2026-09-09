
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.products.models import Category, Product, Unit
from apps.products.services import (
    activate_category,
    activate_product,
    activate_unit,
    create_category,
    create_product,
    create_unit,
    deactivate_category,
    deactivate_product,
    deactivate_unit,
    update_category,
    update_product,
    update_unit,
)


class ProductServiceTests(TestCase):
    """Tests for the Products service layer."""

    def setUp(self):
        self.category = Category.objects.create(
            name="Chocolates",
        )

        self.unit = Unit.objects.create(
            name="Piece",
            symbol="pcs",
        )

        self.product = Product.objects.create(
            name="Chocolate Bar",
            category=self.category,
            unit=self.unit,
            current_purchase_cost=Decimal("1.50"),
            current_sell_price=Decimal("2.50"),
            minimum_stock=Decimal("10"),
            current_stock=Decimal("25"),
        )

    # ---------------------------------------------------------
    # Category tests
    # ---------------------------------------------------------

    def test_create_category(self):
        category = create_category(
            name="Chips",
        )

        self.assertEqual(category.name, "Chips")
        self.assertTrue(category.is_active)

    def test_create_category_rejects_empty_name(self):
        with self.assertRaises(ValidationError):
            create_category(name="   ")

    def test_create_category_rejects_duplicate_name(self):
        with self.assertRaises(ValidationError):
            create_category(name=" chocolates ")

    def test_update_category(self):
        category = update_category(
            category_id=self.category.id,
            name="Premium Chocolates",
        )

        category.refresh_from_db()

        self.assertEqual(
            category.name,
            "Premium Chocolates",
        )

    def test_update_category_rejects_duplicate_name(self):
        Category.objects.create(
            name="Chips",
        )

        with self.assertRaises(ValidationError):
            update_category(
                category_id=self.category.id,
                name="Chips",
            )

    def test_deactivate_category(self):
        category = deactivate_category(
            category_id=self.category.id,
        )

        category.refresh_from_db()

        self.assertFalse(category.is_active)

    def test_activate_category(self):
        self.category.is_active = False
        self.category.save()

        category = activate_category(
            category_id=self.category.id,
        )

        category.refresh_from_db()

        self.assertTrue(category.is_active)

    # ---------------------------------------------------------
    # Unit tests
    # ---------------------------------------------------------

    def test_create_unit(self):
        unit = create_unit(
            name="Kilogram",
            symbol="kg",
        )

        self.assertEqual(unit.name, "Kilogram")
        self.assertEqual(unit.symbol, "kg")
        self.assertTrue(unit.is_active)

    def test_create_unit_rejects_empty_name(self):
        with self.assertRaises(ValidationError):
            create_unit(
                name="   ",
                symbol="kg",
            )

    def test_create_unit_rejects_empty_symbol(self):
        with self.assertRaises(ValidationError):
            create_unit(
                name="Kilogram",
                symbol="   ",
            )

    def test_create_unit_rejects_duplicate_name(self):
        with self.assertRaises(ValidationError):
            create_unit(
                name=" piece ",
                symbol="unit",
            )

    def test_create_unit_rejects_duplicate_symbol(self):
        with self.assertRaises(ValidationError):
            create_unit(
                name="Another Unit",
                symbol="PCS",
            )

    def test_update_unit(self):
        unit = update_unit(
            unit_id=self.unit.id,
            name="Pieces",
            symbol="pc",
        )

        unit.refresh_from_db()

        self.assertEqual(unit.name, "Pieces")
        self.assertEqual(unit.symbol, "pc")

    def test_update_unit_rejects_duplicate_name(self):
        Unit.objects.create(
            name="Kilogram",
            symbol="kg",
        )

        with self.assertRaises(ValidationError):
            update_unit(
                unit_id=self.unit.id,
                name="Kilogram",
                symbol="pc",
            )

    def test_update_unit_rejects_duplicate_symbol(self):
        Unit.objects.create(
            name="Kilogram",
            symbol="kg",
        )

        with self.assertRaises(ValidationError):
            update_unit(
                unit_id=self.unit.id,
                name="Pieces",
                symbol="kg",
            )

    def test_deactivate_unit(self):
        unit = deactivate_unit(
            unit_id=self.unit.id,
        )

        unit.refresh_from_db()

        self.assertFalse(unit.is_active)

    def test_activate_unit(self):
        self.unit.is_active = False
        self.unit.save()

        unit = activate_unit(
            unit_id=self.unit.id,
        )

        unit.refresh_from_db()

        self.assertTrue(unit.is_active)

    # ---------------------------------------------------------
    # Product creation tests
    # ---------------------------------------------------------

    def test_create_product(self):
        product = create_product(
            name="Potato Chips",
            category_id=self.category.id,
            unit_id=self.unit.id,
            current_purchase_cost="2.00",
            current_sell_price="3.50",
            minimum_stock="15",
        )

        self.assertEqual(
            product.name,
            "Potato Chips",
        )

        self.assertEqual(
            product.current_purchase_cost,
            Decimal("2.00"),
        )

        self.assertEqual(
            product.current_sell_price,
            Decimal("3.50"),
        )

        self.assertEqual(
            product.minimum_stock,
            Decimal("15"),
        )

        # New products start with zero stock.
        self.assertEqual(
            product.current_stock,
            Decimal("0"),
        )

        self.assertTrue(product.is_active)

    def test_create_product_rejects_empty_name(self):
        with self.assertRaises(ValidationError):
            create_product(
                name="   ",
                category_id=self.category.id,
                unit_id=self.unit.id,
                current_purchase_cost="1.00",
                current_sell_price="2.00",
                minimum_stock="10",
            )

    def test_create_product_rejects_negative_purchase_cost(self):
        with self.assertRaises(ValidationError):
            create_product(
                name="Invalid Product",
                category_id=self.category.id,
                unit_id=self.unit.id,
                current_purchase_cost="-1.00",
                current_sell_price="2.00",
                minimum_stock="10",
            )

    def test_create_product_rejects_negative_sell_price(self):
        with self.assertRaises(ValidationError):
            create_product(
                name="Invalid Product",
                category_id=self.category.id,
                unit_id=self.unit.id,
                current_purchase_cost="1.00",
                current_sell_price="-2.00",
                minimum_stock="10",
            )

    def test_create_product_rejects_negative_minimum_stock(self):
        with self.assertRaises(ValidationError):
            create_product(
                name="Invalid Product",
                category_id=self.category.id,
                unit_id=self.unit.id,
                current_purchase_cost="1.00",
                current_sell_price="2.00",
                minimum_stock="-10",
            )

    def test_create_product_rejects_inactive_category(self):
        self.category.is_active = False
        self.category.save()

        with self.assertRaises(ValidationError):
            create_product(
                name="Invalid Product",
                category_id=self.category.id,
                unit_id=self.unit.id,
                current_purchase_cost="1.00",
                current_sell_price="2.00",
                minimum_stock="10",
            )

    def test_create_product_rejects_inactive_unit(self):
        self.unit.is_active = False
        self.unit.save()

        with self.assertRaises(ValidationError):
            create_product(
                name="Invalid Product",
                category_id=self.category.id,
                unit_id=self.unit.id,
                current_purchase_cost="1.00",
                current_sell_price="2.00",
                minimum_stock="10",
            )

    # ---------------------------------------------------------
    # Product update tests
    # ---------------------------------------------------------

    def test_update_product(self):
        product = update_product(
            product_id=self.product.id,
            name="Premium Chocolate Bar",
            category_id=self.category.id,
            unit_id=self.unit.id,
            current_purchase_cost="1.75",
            current_sell_price="3.00",
            minimum_stock="12",
        )

        product.refresh_from_db()

        self.assertEqual(
            product.name,
            "Premium Chocolate Bar",
        )

        self.assertEqual(
            product.current_purchase_cost,
            Decimal("1.75"),
        )

        self.assertEqual(
            product.current_sell_price,
            Decimal("3.00"),
        )

        self.assertEqual(
            product.minimum_stock,
            Decimal("12"),
        )

    def test_update_product_does_not_change_stock(self):
        original_stock = self.product.current_stock

        update_product(
            product_id=self.product.id,
            name="Updated Chocolate",
            category_id=self.category.id,
            unit_id=self.unit.id,
            current_purchase_cost="2.00",
            current_sell_price="3.50",
            minimum_stock="15",
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.current_stock,
            original_stock,
        )

    def test_update_product_rejects_inactive_category(self):
        self.category.is_active = False
        self.category.save()

        with self.assertRaises(ValidationError):
            update_product(
                product_id=self.product.id,
                name="Updated Chocolate",
                category_id=self.category.id,
                unit_id=self.unit.id,
                current_purchase_cost="2.00",
                current_sell_price="3.50",
                minimum_stock="15",
            )

    def test_update_product_rejects_inactive_unit(self):
        self.unit.is_active = False
        self.unit.save()

        with self.assertRaises(ValidationError):
            update_product(
                product_id=self.product.id,
                name="Updated Chocolate",
                category_id=self.category.id,
                unit_id=self.unit.id,
                current_purchase_cost="2.00",
                current_sell_price="3.50",
                minimum_stock="15",
            )

    # ---------------------------------------------------------
    # Product activation tests
    # ---------------------------------------------------------

    def test_deactivate_product(self):
        product = deactivate_product(
            product_id=self.product.id,
        )

        product.refresh_from_db()

        self.assertFalse(product.is_active)

    def test_activate_product(self):
        self.product.is_active = False
        self.product.save()

        product = activate_product(
            product_id=self.product.id,
        )

        product.refresh_from_db()

        self.assertTrue(product.is_active)
