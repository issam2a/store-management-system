from datetime import date, datetime, timezone
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.products.models import Category, Product, Unit
from apps.sales.models import Sale, SaleItem
from django.utils import timezone as django_timezone
from .services import (
    get_profitability_summary,
    get_top_selling_products,
    get_slow_moving_products,
    get_product_profitability,
    get_sales_trend,
)
User = get_user_model()

class ProfitabilityAnalyticsTestCase(TestCase):


    def setUp(self):
        self.user = User.objects.create_user(
            username="analytics_test_user",
            password="testpass123",
        )

        self.category = Category.objects.create(
            name="Test Category",
        )

        self.unit = Unit.objects.create(
            name="Piece",
            symbol="pc",
        )

        self.product = Product.objects.create(
            name="Test Product",
            category=self.category,
            unit=self.unit,
            current_purchase_cost=Decimal("50.00"),
            current_sell_price=Decimal("100.00"),
            minimum_stock=Decimal("10.00"),
            current_stock=Decimal("20.00"),
        )

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    def create_completed_sale(
        self,
        reference,
        total_amount,
        subtotal_amount=None,
        discount_amount=None,
        completed_at=None,
    ):
        if subtotal_amount is None:
            subtotal_amount = total_amount

        if discount_amount is None:
            discount_amount = Decimal("0.00")

        sale = Sale.objects.create(
            reference=reference,
            payment_type=Sale.PaymentType.CASH,
            status=Sale.Status.COMPLETED,
            subtotal_amount=subtotal_amount,
            discount_amount=discount_amount,
            total_amount=total_amount,
            created_by=self.user,
            completed_at=completed_at,
        )

        return sale

    def add_sale_item(
        self,
        sale,
        quantity,
        unit_price,
        unit_cost,
    ):
        line_total = (
            quantity * unit_price
        ).quantize(Decimal("0.01"))

        

        return SaleItem.objects.create(
            sale=sale,
            product=self.product,
            quantity=quantity,
            unit_price=unit_price,
            line_total=line_total,
            unit_cost=unit_cost,
            
        )

    # ---------------------------------------------------------
    # Basic Profitability
    # ---------------------------------------------------------

    def test_profitability_summary_returns_zero_when_no_sales_exist(self):
        summary = get_profitability_summary()

        self.assertEqual(
            summary["revenue"],
            Decimal("0.00"),
        )

        self.assertEqual(
            summary["cogs"],
            Decimal("0.00"),
        )

        self.assertEqual(
            summary["gross_profit"],
            Decimal("0.00"),
        )

        self.assertIsNone(
            summary["gross_margin"],
        )

    def test_profitability_summary_calculates_revenue_cogs_and_profit(self):
        sale = self.create_completed_sale(
            reference="SALE-PROFIT-001",
            subtotal_amount=Decimal("1000.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("1000.00"),
        )

        self.add_sale_item(
            sale=sale,
            quantity=Decimal("10.00"),
            unit_price=Decimal("100.00"),
            unit_cost=Decimal("60.00"),
        )

        summary = get_profitability_summary()

        self.assertEqual(
            summary["revenue"],
            Decimal("1000.00"),
        )

        self.assertEqual(
            summary["cogs"],
            Decimal("600.00"),
        )

        self.assertEqual(
            summary["gross_profit"],
            Decimal("400.00"),
        )

        self.assertEqual(
            summary["gross_margin"],
            Decimal("40.00"),
        )

    # ---------------------------------------------------------
    # Loss-Making Sales
    # ---------------------------------------------------------

    def test_profitability_summary_calculates_negative_gross_profit(self):
        sale = self.create_completed_sale(
            reference="SALE-LOSS-001",
            subtotal_amount=Decimal("1000.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("1000.00"),
        )

        self.add_sale_item(
            sale=sale,
            quantity=Decimal("10.00"),
            unit_price=Decimal("100.00"),
            unit_cost=Decimal("120.00"),
        )

        summary = get_profitability_summary()

        self.assertEqual(
            summary["revenue"],
            Decimal("1000.00"),
        )

        self.assertEqual(
            summary["cogs"],
            Decimal("1200.00"),
        )

        self.assertEqual(
            summary["gross_profit"],
            Decimal("-200.00"),
        )

        self.assertEqual(
            summary["gross_margin"],
            Decimal("-20.00"),
        )

    # ---------------------------------------------------------
    # Zero Revenue With COGS
    # ---------------------------------------------------------

    def test_profitability_summary_returns_undefined_margin_when_revenue_is_zero_and_cogs_exist(
        self,
    ):
        sale = self.create_completed_sale(
            reference="SALE-DISCOUNT-001",
            subtotal_amount=Decimal("100.00"),
            discount_amount=Decimal("100.00"),
            total_amount=Decimal("0.00"),
        )

        self.add_sale_item(
            sale=sale,
            quantity=Decimal("1.00"),
            unit_price=Decimal("100.00"),
            unit_cost=Decimal("50.00"),
        )

        summary = get_profitability_summary()

        self.assertEqual(
            summary["revenue"],
            Decimal("0.00"),
        )

        self.assertEqual(
            summary["cogs"],
            Decimal("50.00"),
        )

        self.assertEqual(
            summary["gross_profit"],
            Decimal("-50.00"),
        )

        self.assertIsNone(
            summary["gross_margin"],
        )

    # ---------------------------------------------------------
    # Multiple Sale Items
    # ---------------------------------------------------------

    def test_profitability_summary_does_not_multiply_revenue_for_multiple_items(
        self,
    ):
        sale = self.create_completed_sale(
            reference="SALE-MULTI-001",
            subtotal_amount=Decimal("1200.00"),
            discount_amount=Decimal("200.00"),
            total_amount=Decimal("1000.00"),
        )

        self.add_sale_item(
            sale=sale,
            quantity=Decimal("4.00"),
            unit_price=Decimal("150.00"),
            unit_cost=Decimal("50.00"),
        )

        self.add_sale_item(
            sale=sale,
            quantity=Decimal("2.00"),
            unit_price=Decimal("300.00"),
            unit_cost=Decimal("200.00"),
        )

        summary = get_profitability_summary()

        self.assertEqual(
            summary["revenue"],
            Decimal("1000.00"),
        )

        self.assertEqual(
            summary["cogs"],
            Decimal("600.00"),
        )

        self.assertEqual(
            summary["gross_profit"],
            Decimal("400.00"),
        )

        self.assertEqual(
            summary["gross_margin"],
            Decimal("40.00"),
        )

    # ---------------------------------------------------------
    # Sale Status
    # ---------------------------------------------------------

    def test_profitability_summary_excludes_draft_sales(self):
        sale = Sale.objects.create(
            reference="SALE-DRAFT-001",
            payment_type=Sale.PaymentType.CASH,
            status=Sale.Status.DRAFT,
            subtotal_amount=Decimal("1000.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("1000.00"),
            created_by=self.user,
        )

        self.add_sale_item(
            sale=sale,
            quantity=Decimal("10.00"),
            unit_price=Decimal("100.00"),
            unit_cost=Decimal("50.00"),
        )

        summary = get_profitability_summary()

        self.assertEqual(
            summary["revenue"],
            Decimal("0.00"),
        )

        self.assertEqual(
            summary["cogs"],
            Decimal("0.00"),
        )

        self.assertEqual(
            summary["gross_profit"],
            Decimal("0.00"),
        )

        self.assertIsNone(
            summary["gross_margin"],
        )

    def test_profitability_summary_excludes_cancelled_sales(self):
        sale = Sale.objects.create(
            reference="SALE-CANCEL-001",
            payment_type=Sale.PaymentType.CASH,
            status=Sale.Status.CANCELLED,
            subtotal_amount=Decimal("1000.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("1000.00"),
            created_by=self.user,
        )

        self.add_sale_item(
            sale=sale,
            quantity=Decimal("10.00"),
            unit_price=Decimal("100.00"),
            unit_cost=Decimal("50.00"),
        )

        summary = get_profitability_summary()

        self.assertEqual(
            summary["revenue"],
            Decimal("0.00"),
        )

        self.assertEqual(
            summary["cogs"],
            Decimal("0.00"),
        )

        self.assertEqual(
            summary["gross_profit"],
            Decimal("0.00"),
        )

        self.assertIsNone(
            summary["gross_margin"],
        )

    # ---------------------------------------------------------
    # Discounts
    # ---------------------------------------------------------

    def test_profitability_summary_uses_final_sale_total_as_revenue(self):
        sale = self.create_completed_sale(
            reference="SALE-DISCOUNT-002",
            subtotal_amount=Decimal("1000.00"),
            discount_amount=Decimal("200.00"),
            total_amount=Decimal("800.00"),
        )

        self.add_sale_item(
            sale=sale,
            quantity=Decimal("10.00"),
            unit_price=Decimal("100.00"),
            unit_cost=Decimal("50.00"),
        )

        summary = get_profitability_summary()

        self.assertEqual(
            summary["revenue"],
            Decimal("800.00"),
        )

        self.assertEqual(
            summary["cogs"],
            Decimal("500.00"),
        )

        self.assertEqual(
            summary["gross_profit"],
            Decimal("300.00"),
        )

        self.assertEqual(
            summary["gross_margin"],
            Decimal("37.50"),
        )

    # ---------------------------------------------------------
    # Date Filtering
    # ---------------------------------------------------------

    def test_profitability_summary_filters_by_start_date(self):
        sale_before = self.create_completed_sale(
            reference="SALE-DATE-001",
            total_amount=Decimal("100.00"),
            completed_at=datetime(
                2026,
                8,
                31,
                12,
                0,
                tzinfo=timezone.utc,
            ),
        )

        self.add_sale_item(
            sale=sale_before,
            quantity=Decimal("1.00"),
            unit_price=Decimal("100.00"),
            unit_cost=Decimal("50.00"),
        )

        sale_on_date = self.create_completed_sale(
            reference="SALE-DATE-002",
            total_amount=Decimal("200.00"),
            completed_at=datetime(
                2026,
                9,
                1,
                12,
                0,
                tzinfo=timezone.utc,
            ),
        )

        self.add_sale_item(
            sale=sale_on_date,
            quantity=Decimal("2.00"),
            unit_price=Decimal("100.00"),
            unit_cost=Decimal("50.00"),
        )

        summary = get_profitability_summary(
            start_date=date(2026, 9, 1),
        )

        self.assertEqual(
            summary["revenue"],
            Decimal("200.00"),
        )

        self.assertEqual(
            summary["cogs"],
            Decimal("100.00"),
        )

        self.assertEqual(
            summary["gross_profit"],
            Decimal("100.00"),
        )

    def test_profitability_summary_filters_by_end_date(self):
        sale_on_date = self.create_completed_sale(
            reference="SALE-DATE-003",
            total_amount=Decimal("200.00"),
            completed_at=datetime(
                2026,
                9,
                1,
                12,
                0,
                tzinfo=timezone.utc,
            ),
        )

        self.add_sale_item(
            sale=sale_on_date,
            quantity=Decimal("2.00"),
            unit_price=Decimal("100.00"),
            unit_cost=Decimal("50.00"),
        )

        sale_after = self.create_completed_sale(
            reference="SALE-DATE-004",
            total_amount=Decimal("300.00"),
            completed_at=datetime(
                2026,
                9,
                2,
                12,
                0,
                tzinfo=timezone.utc,
            ),
        )

        self.add_sale_item(
            sale=sale_after,
            quantity=Decimal("3.00"),
            unit_price=Decimal("100.00"),
            unit_cost=Decimal("50.00"),
        )

        summary = get_profitability_summary(
            end_date=date(2026, 9, 1),
        )

        self.assertEqual(
            summary["revenue"],
            Decimal("200.00"),
        )

        self.assertEqual(
            summary["cogs"],
            Decimal("100.00"),
        )

        self.assertEqual(
            summary["gross_profit"],
            Decimal("100.00"),
        )

    def test_profitability_summary_filters_by_date_range(self):
        sale_before = self.create_completed_sale(
            reference="SALE-DATE-005",
            total_amount=Decimal("100.00"),
            completed_at=datetime(
                2026,
                8,
                31,
                12,
                0,
                tzinfo=timezone.utc,
            ),
        )

        self.add_sale_item(
            sale=sale_before,
            quantity=Decimal("1.00"),
            unit_price=Decimal("100.00"),
            unit_cost=Decimal("50.00"),
        )

        sale_inside = self.create_completed_sale(
            reference="SALE-DATE-006",
            total_amount=Decimal("200.00"),
            completed_at=datetime(
                2026,
                9,
                5,
                12,
                0,
                tzinfo=timezone.utc,
            ),
        )

        self.add_sale_item(
            sale=sale_inside,
            quantity=Decimal("2.00"),
            unit_price=Decimal("100.00"),
            unit_cost=Decimal("50.00"),
        )

        sale_after = self.create_completed_sale(
            reference="SALE-DATE-007",
            total_amount=Decimal("300.00"),
            completed_at=datetime(
                2026,
                9,
                15,
                12,
                0,
                tzinfo=timezone.utc,
            ),
        )

        self.add_sale_item(
            sale=sale_after,
            quantity=Decimal("3.00"),
            unit_price=Decimal("100.00"),
            unit_cost=Decimal("50.00"),
        )

        summary = get_profitability_summary(
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 10),
        )

        self.assertEqual(
            summary["revenue"],
            Decimal("200.00"),
        )

        self.assertEqual(
            summary["cogs"],
            Decimal("100.00"),
        )

        self.assertEqual(
            summary["gross_profit"],
            Decimal("100.00"),
        )

        self.assertEqual(
            summary["gross_margin"],
            Decimal("50.00"),
        )

    # ---------------------------------------------------------
    # Top-Selling Products
    # ---------------------------------------------------------

    def test_top_selling_products_returns_empty_list_when_no_sales_exist(self):
        result = get_top_selling_products()

        self.assertEqual(result, [])


    def test_top_selling_products_ranks_products_by_quantity_sold(self):
        product_2 = Product.objects.create(
            name="Product 2",
            category=self.category,
            unit=self.unit,
            current_purchase_cost=Decimal("30.00"),
            current_sell_price=Decimal("60.00"),
            minimum_stock=Decimal("10.00"),
            current_stock=Decimal("20.00"),
        )

        product_3 = Product.objects.create(
            name="Product 3",
            category=self.category,
            unit=self.unit,
            current_purchase_cost=Decimal("20.00"),
            current_sell_price=Decimal("40.00"),
            minimum_stock=Decimal("10.00"),
            current_stock=Decimal("20.00"),
        )

        sale = self.create_completed_sale(
            reference="SALE-TOP-001",
            total_amount=Decimal("600.00"),
        )

        SaleItem.objects.create(
            sale=sale,
            product=self.product,
            quantity=Decimal("5.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("500.00"),
            unit_cost=Decimal("50.00"),
        )

        SaleItem.objects.create(
            sale=sale,
            product=product_2,
            quantity=Decimal("10.00"),
            unit_price=Decimal("60.00"),
            line_total=Decimal("600.00"),
            unit_cost=Decimal("30.00"),
        )

        SaleItem.objects.create(
            sale=sale,
            product=product_3,
            quantity=Decimal("2.00"),
            unit_price=Decimal("40.00"),
            line_total=Decimal("80.00"),
            unit_cost=Decimal("20.00"),
        )

        result = get_top_selling_products()

        self.assertEqual(len(result), 3)

        self.assertEqual(
            result[0]["product_id"],
            product_2.id,
        )
        self.assertEqual(
            result[0]["quantity_sold"],
            Decimal("10.00"),
        )

        self.assertEqual(
            result[1]["product_id"],
            self.product.id,
        )
        self.assertEqual(
            result[1]["quantity_sold"],
            Decimal("5.00"),
        )

        self.assertEqual(
            result[2]["product_id"],
            product_3.id,
        )
        self.assertEqual(
            result[2]["quantity_sold"],
            Decimal("2.00"),
        )


    def test_top_selling_products_sums_quantity_across_multiple_sales(self):
        sale_1 = self.create_completed_sale(
            reference="SALE-TOP-002",
            total_amount=Decimal("300.00"),
        )

        sale_2 = self.create_completed_sale(
            reference="SALE-TOP-003",
            total_amount=Decimal("400.00"),
        )

        SaleItem.objects.create(
            sale=sale_1,
            product=self.product,
            quantity=Decimal("3.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("300.00"),
            unit_cost=Decimal("50.00"),
        )

        SaleItem.objects.create(
            sale=sale_2,
            product=self.product,
            quantity=Decimal("4.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("400.00"),
            unit_cost=Decimal("50.00"),
        )

        result = get_top_selling_products()

        self.assertEqual(len(result), 1)

        self.assertEqual(
            result[0]["quantity_sold"],
            Decimal("7.00"),
        )


    def test_top_selling_products_counts_distinct_sales(self):
        sale_1 = self.create_completed_sale(
            reference="SALE-TOP-004",
            total_amount=Decimal("300.00"),
        )

        sale_2 = self.create_completed_sale(
            reference="SALE-TOP-005",
            total_amount=Decimal("400.00"),
        )

        # Same product appears twice in the same sale.
        SaleItem.objects.create(
            sale=sale_1,
            product=self.product,
            quantity=Decimal("2.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("200.00"),
            unit_cost=Decimal("50.00"),
        )

        SaleItem.objects.create(
            sale=sale_1,
            product=self.product,
            quantity=Decimal("1.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("100.00"),
            unit_cost=Decimal("50.00"),
        )

        SaleItem.objects.create(
            sale=sale_2,
            product=self.product,
            quantity=Decimal("4.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("400.00"),
            unit_cost=Decimal("50.00"),
        )

        result = get_top_selling_products()

        self.assertEqual(len(result), 1)

        self.assertEqual(
            result[0]["quantity_sold"],
            Decimal("7.00"),
        )

        self.assertEqual(
            result[0]["sales_count"],
            2,
        )


    def test_top_selling_products_calculates_gross_sales_value_from_line_total(
        self,
    ):
        sale_1 = self.create_completed_sale(
            reference="SALE-TOP-006",
            subtotal_amount=Decimal("500.00"),
            discount_amount=Decimal("100.00"),
            total_amount=Decimal("400.00"),
        )

        sale_2 = self.create_completed_sale(
            reference="SALE-TOP-007",
            subtotal_amount=Decimal("300.00"),
            discount_amount=Decimal("50.00"),
            total_amount=Decimal("250.00"),
        )

        SaleItem.objects.create(
            sale=sale_1,
            product=self.product,
            quantity=Decimal("5.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("500.00"),
            unit_cost=Decimal("50.00"),
        )

        SaleItem.objects.create(
            sale=sale_2,
            product=self.product,
            quantity=Decimal("3.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("300.00"),
            unit_cost=Decimal("50.00"),
        )

        result = get_top_selling_products()

        self.assertEqual(len(result), 1)

        # Gross sales value is based on line_total,
        # before sale-level discounts.
        self.assertEqual(
            result[0]["gross_sales_value"],
            Decimal("800.00"),
        )


    def test_top_selling_products_excludes_draft_sales(self):
        completed_sale = self.create_completed_sale(
            reference="SALE-TOP-008",
            total_amount=Decimal("300.00"),
        )

        draft_sale = Sale.objects.create(
            reference="SALE-TOP-009",
            payment_type=Sale.PaymentType.CASH,
            status=Sale.Status.DRAFT,
            subtotal_amount=Decimal("1000.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("1000.00"),
            created_by=self.user,
        )

        SaleItem.objects.create(
            sale=completed_sale,
            product=self.product,
            quantity=Decimal("3.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("300.00"),
            unit_cost=Decimal("50.00"),
        )

        SaleItem.objects.create(
            sale=draft_sale,
            product=self.product,
            quantity=Decimal("10.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("1000.00"),
            unit_cost=Decimal("50.00"),
        )

        result = get_top_selling_products()

        self.assertEqual(len(result), 1)

        self.assertEqual(
            result[0]["quantity_sold"],
            Decimal("3.00"),
        )


    def test_top_selling_products_excludes_cancelled_sales(self):
        completed_sale = self.create_completed_sale(
            reference="SALE-TOP-010",
            total_amount=Decimal("300.00"),
        )

        cancelled_sale = Sale.objects.create(
            reference="SALE-TOP-011",
            payment_type=Sale.PaymentType.CASH,
            status=Sale.Status.CANCELLED,
            subtotal_amount=Decimal("1000.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("1000.00"),
            created_by=self.user,
        )

        SaleItem.objects.create(
            sale=completed_sale,
            product=self.product,
            quantity=Decimal("3.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("300.00"),
            unit_cost=Decimal("50.00"),
        )

        SaleItem.objects.create(
            sale=cancelled_sale,
            product=self.product,
            quantity=Decimal("10.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("1000.00"),
            unit_cost=Decimal("50.00"),
        )

        result = get_top_selling_products()

        self.assertEqual(len(result), 1)

        self.assertEqual(
            result[0]["quantity_sold"],
            Decimal("3.00"),
        )


    def test_top_selling_products_respects_limit(self):
        products = []

        for index in range(3):
            product = Product.objects.create(
                name=f"Top Product {index}",
                category=self.category,
                unit=self.unit,
                current_purchase_cost=Decimal("20.00"),
                current_sell_price=Decimal("40.00"),
                minimum_stock=Decimal("10.00"),
                current_stock=Decimal("20.00"),
            )

            products.append(product)

        sale = self.create_completed_sale(
            reference="SALE-TOP-012",
            total_amount=Decimal("600.00"),
        )

        SaleItem.objects.create(
            sale=sale,
            product=products[0],
            quantity=Decimal("10.00"),
            unit_price=Decimal("40.00"),
            line_total=Decimal("400.00"),
            unit_cost=Decimal("20.00"),
        )

        SaleItem.objects.create(
            sale=sale,
            product=products[1],
            quantity=Decimal("8.00"),
            unit_price=Decimal("40.00"),
            line_total=Decimal("320.00"),
            unit_cost=Decimal("20.00"),
        )

        SaleItem.objects.create(
            sale=sale,
            product=products[2],
            quantity=Decimal("5.00"),
            unit_price=Decimal("40.00"),
            line_total=Decimal("200.00"),
            unit_cost=Decimal("20.00"),
        )

        result = get_top_selling_products(limit=2)

        self.assertEqual(len(result), 2)

        self.assertEqual(
            result[0]["product_id"],
            products[0].id,
        )

        self.assertEqual(
            result[1]["product_id"],
            products[1].id,
        )


    def test_top_selling_products_filters_by_start_date(self):
        sale_before = self.create_completed_sale(
            reference="SALE-TOP-013",
            total_amount=Decimal("300.00"),
            completed_at=datetime(
                2026,
                8,
                31,
                12,
                0,
                tzinfo=timezone.utc,
            ),
        )

        sale_on_date = self.create_completed_sale(
            reference="SALE-TOP-014",
            total_amount=Decimal("500.00"),
            completed_at=datetime(
                2026,
                9,
                1,
                12,
                0,
                tzinfo=timezone.utc,
            ),
        )

        SaleItem.objects.create(
            sale=sale_before,
            product=self.product,
            quantity=Decimal("3.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("300.00"),
            unit_cost=Decimal("50.00"),
        )

        SaleItem.objects.create(
            sale=sale_on_date,
            product=self.product,
            quantity=Decimal("5.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("500.00"),
            unit_cost=Decimal("50.00"),
        )

        result = get_top_selling_products(
            start_date=date(2026, 9, 1),
        )

        self.assertEqual(len(result), 1)

        self.assertEqual(
            result[0]["quantity_sold"],
            Decimal("5.00"),
        )


    def test_top_selling_products_filters_by_end_date(self):
        sale_on_date = self.create_completed_sale(
            reference="SALE-TOP-015",
            total_amount=Decimal("500.00"),
            completed_at=datetime(
                2026,
                9,
                1,
                12,
                0,
                tzinfo=timezone.utc,
            ),
        )

        sale_after = self.create_completed_sale(
            reference="SALE-TOP-016",
            total_amount=Decimal("700.00"),
            completed_at=datetime(
                2026,
                9,
                2,
                12,
                0,
                tzinfo=timezone.utc,
            ),
        )

        SaleItem.objects.create(
            sale=sale_on_date,
            product=self.product,
            quantity=Decimal("5.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("500.00"),
            unit_cost=Decimal("50.00"),
        )

        SaleItem.objects.create(
            sale=sale_after,
            product=self.product,
            quantity=Decimal("7.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("700.00"),
            unit_cost=Decimal("50.00"),
        )

        result = get_top_selling_products(
            end_date=date(2026, 9, 1),
        )

        self.assertEqual(len(result), 1)

        self.assertEqual(
            result[0]["quantity_sold"],
            Decimal("5.00"),
        )


    def test_top_selling_products_filters_by_date_range(self):
        sale_before = self.create_completed_sale(
            reference="SALE-TOP-017",
            total_amount=Decimal("300.00"),
            completed_at=datetime(
                2026,
                8,
                31,
                12,
                0,
                tzinfo=timezone.utc,
            ),
        )

        sale_inside = self.create_completed_sale(
            reference="SALE-TOP-018",
            total_amount=Decimal("500.00"),
            completed_at=datetime(
                2026,
                9,
                5,
                12,
                0,
                tzinfo=timezone.utc,
            ),
        )

        sale_after = self.create_completed_sale(
            reference="SALE-TOP-019",
            total_amount=Decimal("700.00"),
            completed_at=datetime(
                2026,
                9,
                15,
                12,
                0,
                tzinfo=timezone.utc,
            ),
        )

        SaleItem.objects.create(
            sale=sale_before,
            product=self.product,
            quantity=Decimal("3.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("300.00"),
            unit_cost=Decimal("50.00"),
        )

        SaleItem.objects.create(
            sale=sale_inside,
            product=self.product,
            quantity=Decimal("5.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("500.00"),
            unit_cost=Decimal("50.00"),
        )

        SaleItem.objects.create(
            sale=sale_after,
            product=self.product,
            quantity=Decimal("7.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("700.00"),
            unit_cost=Decimal("50.00"),
        )

        result = get_top_selling_products(
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 10),
        )

        self.assertEqual(len(result), 1)

        self.assertEqual(
            result[0]["quantity_sold"],
            Decimal("5.00"),
        )

        self.assertEqual(
            result[0]["gross_sales_value"],
            Decimal("500.00"),
        )

    # ---------------------------------------------------------
    # Slow-Moving Products
    # ---------------------------------------------------------

    def test_slow_moving_products_returns_empty_list_when_no_sales_exist(
        self,
    ):
        result = get_slow_moving_products()

        self.assertEqual(result, [])


    def test_slow_moving_products_ranks_products_by_lowest_quantity_sold(
        self,
    ):
        product_2 = Product.objects.create(
            name="Product 2",
            category=self.category,
            unit=self.unit,
            current_purchase_cost=Decimal("30.00"),
            current_sell_price=Decimal("60.00"),
            minimum_stock=Decimal("10.00"),
            current_stock=Decimal("20.00"),
        )

        product_3 = Product.objects.create(
            name="Product 3",
            category=self.category,
            unit=self.unit,
            current_purchase_cost=Decimal("20.00"),
            current_sell_price=Decimal("40.00"),
            minimum_stock=Decimal("10.00"),
            current_stock=Decimal("20.00"),
        )

        sale = self.create_completed_sale(
            reference="SALE-SLOW-001",
            total_amount=Decimal("1000.00"),
        )

        SaleItem.objects.create(
            sale=sale,
            product=self.product,
            quantity=Decimal("10.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("1000.00"),
            unit_cost=Decimal("50.00"),
        )

        SaleItem.objects.create(
            sale=sale,
            product=product_2,
            quantity=Decimal("2.00"),
            unit_price=Decimal("60.00"),
            line_total=Decimal("120.00"),
            unit_cost=Decimal("30.00"),
        )

        SaleItem.objects.create(
            sale=sale,
            product=product_3,
            quantity=Decimal("5.00"),
            unit_price=Decimal("40.00"),
            line_total=Decimal("200.00"),
            unit_cost=Decimal("20.00"),
        )

        result = get_slow_moving_products()

        self.assertEqual(len(result), 3)

        self.assertEqual(
            result[0]["product_id"],
            product_2.id,
        )

        self.assertEqual(
            result[0]["quantity_sold"],
            Decimal("2.00"),
        )

        self.assertEqual(
            result[1]["product_id"],
            product_3.id,
        )

        self.assertEqual(
            result[1]["quantity_sold"],
            Decimal("5.00"),
        )

        self.assertEqual(
            result[2]["product_id"],
            self.product.id,
        )

        self.assertEqual(
            result[2]["quantity_sold"],
            Decimal("10.00"),
        )


    def test_slow_moving_products_sums_quantity_across_multiple_sales(
        self,
    ):
        sale_1 = self.create_completed_sale(
            reference="SALE-SLOW-002",
            total_amount=Decimal("100.00"),
        )

        sale_2 = self.create_completed_sale(
            reference="SALE-SLOW-003",
            total_amount=Decimal("200.00"),
        )

        SaleItem.objects.create(
            sale=sale_1,
            product=self.product,
            quantity=Decimal("1.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("100.00"),
            unit_cost=Decimal("50.00"),
        )

        SaleItem.objects.create(
            sale=sale_2,
            product=self.product,
            quantity=Decimal("2.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("200.00"),
            unit_cost=Decimal("50.00"),
        )

        result = get_slow_moving_products()

        self.assertEqual(len(result), 1)

        self.assertEqual(
            result[0]["quantity_sold"],
            Decimal("3.00"),
        )


    def test_slow_moving_products_counts_distinct_sales(
        self,
    ):
        sale_1 = self.create_completed_sale(
            reference="SALE-SLOW-004",
            total_amount=Decimal("300.00"),
        )

        sale_2 = self.create_completed_sale(
            reference="SALE-SLOW-005",
            total_amount=Decimal("400.00"),
        )

        # Same product appears twice in the same sale.
        SaleItem.objects.create(
            sale=sale_1,
            product=self.product,
            quantity=Decimal("1.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("100.00"),
            unit_cost=Decimal("50.00"),
        )

        SaleItem.objects.create(
            sale=sale_1,
            product=self.product,
            quantity=Decimal("1.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("100.00"),
            unit_cost=Decimal("50.00"),
        )

        SaleItem.objects.create(
            sale=sale_2,
            product=self.product,
            quantity=Decimal("2.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("200.00"),
            unit_cost=Decimal("50.00"),
        )

        result = get_slow_moving_products()

        self.assertEqual(len(result), 1)

        self.assertEqual(
            result[0]["quantity_sold"],
            Decimal("4.00"),
        )

        self.assertEqual(
            result[0]["sales_count"],
            2,
        )


    def test_slow_moving_products_excludes_draft_sales(self):
        completed_sale = self.create_completed_sale(
            reference="SALE-SLOW-006",
            total_amount=Decimal("100.00"),
        )

        draft_sale = Sale.objects.create(
            reference="SALE-SLOW-007",
            payment_type=Sale.PaymentType.CASH,
            status=Sale.Status.DRAFT,
            subtotal_amount=Decimal("1000.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("1000.00"),
            created_by=self.user,
        )

        SaleItem.objects.create(
            sale=completed_sale,
            product=self.product,
            quantity=Decimal("1.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("100.00"),
            unit_cost=Decimal("50.00"),
        )

        SaleItem.objects.create(
            sale=draft_sale,
            product=self.product,
            quantity=Decimal("20.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("2000.00"),
            unit_cost=Decimal("50.00"),
        )

        result = get_slow_moving_products()

        self.assertEqual(len(result), 1)

        self.assertEqual(
            result[0]["quantity_sold"],
            Decimal("1.00"),
        )


    def test_slow_moving_products_excludes_cancelled_sales(self):
        completed_sale = self.create_completed_sale(
            reference="SALE-SLOW-008",
            total_amount=Decimal("100.00"),
        )

        cancelled_sale = Sale.objects.create(
            reference="SALE-SLOW-009",
            payment_type=Sale.PaymentType.CASH,
            status=Sale.Status.CANCELLED,
            subtotal_amount=Decimal("1000.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("1000.00"),
            created_by=self.user,
        )

        SaleItem.objects.create(
            sale=completed_sale,
            product=self.product,
            quantity=Decimal("1.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("100.00"),
            unit_cost=Decimal("50.00"),
        )

        SaleItem.objects.create(
            sale=cancelled_sale,
            product=self.product,
            quantity=Decimal("20.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("2000.00"),
            unit_cost=Decimal("50.00"),
        )

        result = get_slow_moving_products()

        self.assertEqual(len(result), 1)

        self.assertEqual(
            result[0]["quantity_sold"],
            Decimal("1.00"),
        )


    def test_slow_moving_products_respects_limit(self):
        products = []

        for index in range(3):
            product = Product.objects.create(
                name=f"Slow Product {index}",
                category=self.category,
                unit=self.unit,
                current_purchase_cost=Decimal("20.00"),
                current_sell_price=Decimal("40.00"),
                minimum_stock=Decimal("10.00"),
                current_stock=Decimal("20.00"),
            )

            products.append(product)

        sale = self.create_completed_sale(
            reference="SALE-SLOW-010",
            total_amount=Decimal("1000.00"),
        )

        SaleItem.objects.create(
            sale=sale,
            product=products[0],
            quantity=Decimal("10.00"),
            unit_price=Decimal("40.00"),
            line_total=Decimal("400.00"),
            unit_cost=Decimal("20.00"),
        )

        SaleItem.objects.create(
            sale=sale,
            product=products[1],
            quantity=Decimal("2.00"),
            unit_price=Decimal("40.00"),
            line_total=Decimal("80.00"),
            unit_cost=Decimal("20.00"),
        )

        SaleItem.objects.create(
            sale=sale,
            product=products[2],
            quantity=Decimal("5.00"),
            unit_price=Decimal("40.00"),
            line_total=Decimal("200.00"),
            unit_cost=Decimal("20.00"),
        )

        result = get_slow_moving_products(limit=2)

        self.assertEqual(len(result), 2)

        self.assertEqual(
            result[0]["product_id"],
            products[1].id,
        )

        self.assertEqual(
            result[1]["product_id"],
            products[2].id,
        )


    def test_slow_moving_products_filters_by_start_date(self):
        sale_before = self.create_completed_sale(
            reference="SALE-SLOW-011",
            total_amount=Decimal("300.00"),
            completed_at=datetime(
                2026,
                8,
                31,
                12,
                0,
                tzinfo=timezone.utc,
            ),
        )

        sale_on_date = self.create_completed_sale(
            reference="SALE-SLOW-012",
            total_amount=Decimal("500.00"),
            completed_at=datetime(
                2026,
                9,
                1,
                12,
                0,
                tzinfo=timezone.utc,
            ),
        )

        SaleItem.objects.create(
            sale=sale_before,
            product=self.product,
            quantity=Decimal("10.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("1000.00"),
            unit_cost=Decimal("50.00"),
        )

        SaleItem.objects.create(
            sale=sale_on_date,
            product=self.product,
            quantity=Decimal("2.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("200.00"),
            unit_cost=Decimal("50.00"),
        )

        result = get_slow_moving_products(
            start_date=date(2026, 9, 1),
        )

        self.assertEqual(len(result), 1)

        self.assertEqual(
            result[0]["quantity_sold"],
            Decimal("2.00"),
        )


    def test_slow_moving_products_filters_by_end_date(self):
        sale_on_date = self.create_completed_sale(
            reference="SALE-SLOW-013",
            total_amount=Decimal("500.00"),
            completed_at=datetime(
                2026,
                9,
                1,
                12,
                0,
                tzinfo=timezone.utc,
            ),
        )

        sale_after = self.create_completed_sale(
            reference="SALE-SLOW-014",
            total_amount=Decimal("700.00"),
            completed_at=datetime(
                2026,
                9,
                2,
                12,
                0,
                tzinfo=timezone.utc,
            ),
        )

        SaleItem.objects.create(
            sale=sale_on_date,
            product=self.product,
            quantity=Decimal("2.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("200.00"),
            unit_cost=Decimal("50.00"),
        )

        SaleItem.objects.create(
            sale=sale_after,
            product=self.product,
            quantity=Decimal("7.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("700.00"),
            unit_cost=Decimal("50.00"),
        )

        result = get_slow_moving_products(
            end_date=date(2026, 9, 1),
        )

        self.assertEqual(len(result), 1)

        self.assertEqual(
            result[0]["quantity_sold"],
            Decimal("2.00"),
        )


    def test_slow_moving_products_filters_by_date_range(self):
        sale_before = self.create_completed_sale(
            reference="SALE-SLOW-015",
            total_amount=Decimal("300.00"),
            completed_at=datetime(
                2026,
                8,
                31,
                12,
                0,
                tzinfo=timezone.utc,
            ),
        )

        sale_inside = self.create_completed_sale(
            reference="SALE-SLOW-016",
            total_amount=Decimal("500.00"),
            completed_at=datetime(
                2026,
                9,
                5,
                12,
                0,
                tzinfo=timezone.utc,
            ),
        )

        sale_after = self.create_completed_sale(
            reference="SALE-SLOW-017",
            total_amount=Decimal("700.00"),
            completed_at=datetime(
                2026,
                9,
                15,
                12,
                0,
                tzinfo=timezone.utc,
            ),
        )

        SaleItem.objects.create(
            sale=sale_before,
            product=self.product,
            quantity=Decimal("10.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("1000.00"),
            unit_cost=Decimal("50.00"),
        )

        SaleItem.objects.create(
            sale=sale_inside,
            product=self.product,
            quantity=Decimal("2.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("200.00"),
            unit_cost=Decimal("50.00"),
        )

        SaleItem.objects.create(
            sale=sale_after,
            product=self.product,
            quantity=Decimal("7.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("700.00"),
            unit_cost=Decimal("50.00"),
        )

        result = get_slow_moving_products(
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 10),
        )

        self.assertEqual(len(result), 1)

        self.assertEqual(
            result[0]["quantity_sold"],
            Decimal("2.00"),
        )

        self.assertEqual(
            result[0]["gross_sales_value"],
            Decimal("200.00"),
        )


    # ---------------------------------------------------------
    # Product Profitability
    # ---------------------------------------------------------

    def test_product_profitability_returns_empty_list_when_no_sales_exist(
        self,
    ):
        result = get_product_profitability()

        self.assertEqual(result, [])


    def test_product_profitability_calculates_gross_sales_cogs_and_profit(
        self,
    ):
        sale = self.create_completed_sale(
            reference="SALE-PRODUCT-PROFIT-001",
            total_amount=Decimal("1000.00"),
        )

        SaleItem.objects.create(
            sale=sale,
            product=self.product,
            quantity=Decimal("10.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("1000.00"),
            unit_cost=Decimal("60.00"),
        )

        result = get_product_profitability()

        self.assertEqual(len(result), 1)

        product = result[0]

        self.assertEqual(
            product["product_id"],
            self.product.id,
        )

        self.assertEqual(
            product["product__name"],
            self.product.name,
        )

        self.assertEqual(
            product["quantity_sold"],
            Decimal("10.00"),
        )

        self.assertEqual(
            product["gross_sales_value"],
            Decimal("1000.00"),
        )

        self.assertEqual(
            product["cogs"],
            Decimal("600.00"),
        )

        self.assertEqual(
            product["gross_profit"],
            Decimal("400.00"),
        )

        self.assertEqual(
            product["gross_margin"],
            Decimal("40.00"),
        )


    def test_product_profitability_aggregates_multiple_sales(
        self,
    ):
        sale_1 = self.create_completed_sale(
            reference="SALE-PRODUCT-PROFIT-002",
            total_amount=Decimal("500.00"),
        )

        sale_2 = self.create_completed_sale(
            reference="SALE-PRODUCT-PROFIT-003",
            total_amount=Decimal("300.00"),
        )

        SaleItem.objects.create(
            sale=sale_1,
            product=self.product,
            quantity=Decimal("5.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("500.00"),
            unit_cost=Decimal("50.00"),
        )

        SaleItem.objects.create(
            sale=sale_2,
            product=self.product,
            quantity=Decimal("3.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("300.00"),
            unit_cost=Decimal("50.00"),
        )

        result = get_product_profitability()

        self.assertEqual(len(result), 1)

        self.assertEqual(
            result[0]["quantity_sold"],
            Decimal("8.00"),
        )

        self.assertEqual(
            result[0]["gross_sales_value"],
            Decimal("800.00"),
        )

        self.assertEqual(
            result[0]["cogs"],
            Decimal("400.00"),
        )

        self.assertEqual(
            result[0]["gross_profit"],
            Decimal("400.00"),
        )

        self.assertEqual(
            result[0]["gross_margin"],
            Decimal("50.00"),
        )


    def test_product_profitability_uses_sale_item_cost_snapshots(
        self,
    ):
        sale = self.create_completed_sale(
            reference="SALE-PRODUCT-PROFIT-004",
            total_amount=Decimal("1000.00"),
        )

        SaleItem.objects.create(
            sale=sale,
            product=self.product,
            quantity=Decimal("10.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("1000.00"),
            unit_cost=Decimal("70.00"),
        )

        # Change the current product cost after the sale.
        self.product.current_purchase_cost = Decimal("120.00")
        self.product.save(
            update_fields=[
                "current_purchase_cost",
            ]
        )

        result = get_product_profitability()

        self.assertEqual(
            result[0]["cogs"],
            Decimal("700.00"),
        )

        self.assertEqual(
            result[0]["gross_profit"],
            Decimal("300.00"),
        )

        self.assertEqual(
            result[0]["gross_margin"],
            Decimal("30.00"),
        )


    def test_product_profitability_excludes_draft_sales(
        self,
    ):
        completed_sale = self.create_completed_sale(
            reference="SALE-PRODUCT-PROFIT-005",
            total_amount=Decimal("300.00"),
        )

        draft_sale = Sale.objects.create(
            reference="SALE-PRODUCT-PROFIT-006",
            payment_type=Sale.PaymentType.CASH,
            status=Sale.Status.DRAFT,
            subtotal_amount=Decimal("1000.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("1000.00"),
            created_by=self.user,
        )

        SaleItem.objects.create(
            sale=completed_sale,
            product=self.product,
            quantity=Decimal("3.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("300.00"),
            unit_cost=Decimal("50.00"),
        )

        SaleItem.objects.create(
            sale=draft_sale,
            product=self.product,
            quantity=Decimal("20.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("2000.00"),
            unit_cost=Decimal("50.00"),
        )

        result = get_product_profitability()

        self.assertEqual(len(result), 1)

        self.assertEqual(
            result[0]["quantity_sold"],
            Decimal("3.00"),
        )


    def test_product_profitability_excludes_cancelled_sales(
        self,
    ):
        completed_sale = self.create_completed_sale(
            reference="SALE-PRODUCT-PROFIT-007",
            total_amount=Decimal("300.00"),
        )

        cancelled_sale = Sale.objects.create(
            reference="SALE-PRODUCT-PROFIT-008",
            payment_type=Sale.PaymentType.CASH,
            status=Sale.Status.CANCELLED,
            subtotal_amount=Decimal("1000.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("1000.00"),
            created_by=self.user,
        )

        SaleItem.objects.create(
            sale=completed_sale,
            product=self.product,
            quantity=Decimal("3.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("300.00"),
            unit_cost=Decimal("50.00"),
        )

        SaleItem.objects.create(
            sale=cancelled_sale,
            product=self.product,
            quantity=Decimal("20.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("2000.00"),
            unit_cost=Decimal("50.00"),
        )

        result = get_product_profitability()

        self.assertEqual(len(result), 1)

        self.assertEqual(
            result[0]["quantity_sold"],
            Decimal("3.00"),
        )


    def test_product_profitability_handles_loss_making_product(
        self,
    ):
        sale = self.create_completed_sale(
            reference="SALE-PRODUCT-PROFIT-009",
            total_amount=Decimal("500.00"),
        )

        SaleItem.objects.create(
            sale=sale,
            product=self.product,
            quantity=Decimal("5.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("500.00"),
            unit_cost=Decimal("120.00"),
        )

        result = get_product_profitability()

        self.assertEqual(
            result[0]["gross_sales_value"],
            Decimal("500.00"),
        )

        self.assertEqual(
            result[0]["cogs"],
            Decimal("600.00"),
        )

        self.assertEqual(
            result[0]["gross_profit"],
            Decimal("-100.00"),
        )

        self.assertEqual(
            result[0]["gross_margin"],
            Decimal("-20.00"),
        )


    def test_product_profitability_respects_limit(
        self,
    ):
        product_2 = Product.objects.create(
            name="Product 2",
            category=self.category,
            unit=self.unit,
            current_purchase_cost=Decimal("30.00"),
            current_sell_price=Decimal("60.00"),
            minimum_stock=Decimal("10.00"),
            current_stock=Decimal("20.00"),
        )

        product_3 = Product.objects.create(
            name="Product 3",
            category=self.category,
            unit=self.unit,
            current_purchase_cost=Decimal("20.00"),
            current_sell_price=Decimal("40.00"),
            minimum_stock=Decimal("10.00"),
            current_stock=Decimal("20.00"),
        )

        sale = self.create_completed_sale(
            reference="SALE-PRODUCT-PROFIT-010",
            total_amount=Decimal("600.00"),
        )

        SaleItem.objects.create(
            sale=sale,
            product=self.product,
            quantity=Decimal("10.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("1000.00"),
            unit_cost=Decimal("50.00"),
        )

        SaleItem.objects.create(
            sale=sale,
            product=product_2,
            quantity=Decimal("5.00"),
            unit_price=Decimal("60.00"),
            line_total=Decimal("300.00"),
            unit_cost=Decimal("30.00"),
        )

        SaleItem.objects.create(
            sale=sale,
            product=product_3,
            quantity=Decimal("2.00"),
            unit_price=Decimal("40.00"),
            line_total=Decimal("80.00"),
            unit_cost=Decimal("20.00"),
        )

        result = get_product_profitability(limit=2)

        self.assertEqual(len(result), 2)

        self.assertEqual(
            result[0]["product_id"],
            self.product.id,
        )

        self.assertEqual(
            result[1]["product_id"],
            product_2.id,
        )


    def test_product_profitability_filters_by_date_range(
        self,
    ):
        sale_before = self.create_completed_sale(
            reference="SALE-PRODUCT-PROFIT-011",
            total_amount=Decimal("300.00"),
            completed_at=datetime(
                2026,
                8,
                31,
                12,
                0,
                tzinfo=timezone.utc,
            ),
        )

        sale_inside = self.create_completed_sale(
            reference="SALE-PRODUCT-PROFIT-012",
            total_amount=Decimal("500.00"),
            completed_at=datetime(
                2026,
                9,
                5,
                12,
                0,
                tzinfo=timezone.utc,
            ),
        )

        sale_after = self.create_completed_sale(
            reference="SALE-PRODUCT-PROFIT-013",
            total_amount=Decimal("700.00"),
            completed_at=datetime(
                2026,
                9,
                15,
                12,
                0,
                tzinfo=timezone.utc,
            ),
        )

        SaleItem.objects.create(
            sale=sale_before,
            product=self.product,
            quantity=Decimal("3.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("300.00"),
            unit_cost=Decimal("50.00"),
        )

        SaleItem.objects.create(
            sale=sale_inside,
            product=self.product,
            quantity=Decimal("5.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("500.00"),
            unit_cost=Decimal("50.00"),
        )

        SaleItem.objects.create(
            sale=sale_after,
            product=self.product,
            quantity=Decimal("7.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("700.00"),
            unit_cost=Decimal("50.00"),
        )

        result = get_product_profitability(
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 10),
        )

        self.assertEqual(len(result), 1)

        self.assertEqual(
            result[0]["quantity_sold"],
            Decimal("5.00"),
        )

        self.assertEqual(
            result[0]["gross_sales_value"],
            Decimal("500.00"),
        )

        self.assertEqual(
            result[0]["cogs"],
            Decimal("250.00"),
        )

        self.assertEqual(
            result[0]["gross_profit"],
            Decimal("250.00"),
        )

        self.assertEqual(
            result[0]["gross_margin"],
            Decimal("50.00"),
        )

    # ---------------------------------------------------------
    # Sales Trend
    # ---------------------------------------------------------

    def test_sales_trend_returns_empty_list_when_no_sales_exist(self):
        result = get_sales_trend()

        self.assertEqual(result, [])


    def test_sales_trend_daily_aggregation(self):
        completed_at = datetime(
            2026,
            1,
            15,
            10,
            0,
            tzinfo=timezone.utc,
        )

        sale = self.create_completed_sale(
            reference="SALE-001",
            total_amount=Decimal("300.00"),
            completed_at=completed_at,
        )

        self.add_sale_item(
            sale=sale,
            quantity=Decimal("3.000"),
            unit_price=Decimal("100.00"),
            unit_cost=Decimal("50.00"),
        )

        result = get_sales_trend(
            interval="day",
        )

        self.assertEqual(len(result), 1)

        self.assertEqual(
            result[0]["date"],
            date(2026, 1, 15),
        )

        self.assertEqual(
            result[0]["transaction_count"],
            1,
        )

        self.assertEqual(
            result[0]["units_sold"],
            Decimal("3.000"),
        )

        self.assertEqual(
            result[0]["gross_sales_value"],
            Decimal("300.00"),
        )

        self.assertEqual(
            result[0]["revenue"],
            Decimal("300.00"),
        )


    def test_sales_trend_weekly_aggregates_sales_in_same_week(self):
        monday = datetime(
            2026,
            1,
            12,
            10,
            0,
            tzinfo=timezone.utc,
        )

        friday = datetime(
            2026,
            1,
            16,
            15,
            0,
            tzinfo=timezone.utc,
        )

        sale_1 = self.create_completed_sale(
            reference="SALE-001",
            total_amount=Decimal("100.00"),
            completed_at=monday,
        )

        sale_2 = self.create_completed_sale(
            reference="SALE-002",
            total_amount=Decimal("200.00"),
            completed_at=friday,
        )

        self.add_sale_item(
            sale=sale_1,
            quantity=Decimal("2.000"),
            unit_price=Decimal("50.00"),
            unit_cost=Decimal("25.00"),
        )

        self.add_sale_item(
            sale=sale_2,
            quantity=Decimal("4.000"),
            unit_price=Decimal("50.00"),
            unit_cost=Decimal("25.00"),
        )

        result = get_sales_trend(
            interval="week",
        )

        self.assertEqual(len(result), 1)

        self.assertEqual(
            result[0]["date"],
            date(2026, 1, 12),
        )

        self.assertEqual(
            result[0]["transaction_count"],
            2,
        )

        self.assertEqual(
            result[0]["units_sold"],
            Decimal("6.000"),
        )

        self.assertEqual(
            result[0]["gross_sales_value"],
            Decimal("300.00"),
        )

        self.assertEqual(
            result[0]["revenue"],
            Decimal("300.00"),
        )


    def test_sales_trend_monthly_aggregates_sales_in_same_month(self):
        sale_1 = self.create_completed_sale(
            reference="SALE-001",
            total_amount=Decimal("100.00"),
            completed_at=datetime(
                2026,
                2,
                5,
                10,
                0,
                tzinfo=timezone.utc,
            ),
        )

        sale_2 = self.create_completed_sale(
            reference="SALE-002",
            total_amount=Decimal("200.00"),
            completed_at=datetime(
                2026,
                2,
                20,
                15,
                0,
                tzinfo=timezone.utc,
            ),
        )

        self.add_sale_item(
            sale=sale_1,
            quantity=Decimal("2.000"),
            unit_price=Decimal("50.00"),
            unit_cost=Decimal("25.00"),
        )

        self.add_sale_item(
            sale=sale_2,
            quantity=Decimal("4.000"),
            unit_price=Decimal("50.00"),
            unit_cost=Decimal("25.00"),
        )

        result = get_sales_trend(
            interval="month",
        )

        self.assertEqual(len(result), 1)

        self.assertEqual(
            result[0]["date"],
            date(2026, 2, 1),
        )

        self.assertEqual(
            result[0]["transaction_count"],
            2,
        )

        self.assertEqual(
            result[0]["units_sold"],
            Decimal("6.000"),
        )

        self.assertEqual(
            result[0]["gross_sales_value"],
            Decimal("300.00"),
        )

        self.assertEqual(
            result[0]["revenue"],
            Decimal("300.00"),
        )


    def test_sales_trend_monthly_separates_different_months(self):
        sale_1 = self.create_completed_sale(
            reference="SALE-001",
            total_amount=Decimal("100.00"),
            completed_at=datetime(
                2026,
                2,
                15,
                10,
                0,
                tzinfo=timezone.utc,
            ),
        )

        sale_2 = self.create_completed_sale(
            reference="SALE-002",
            total_amount=Decimal("200.00"),
            completed_at=datetime(
                2026,
                3,
                15,
                10,
                0,
                tzinfo=timezone.utc,
            ),
        )

        self.add_sale_item(
            sale=sale_1,
            quantity=Decimal("2.000"),
            unit_price=Decimal("50.00"),
            unit_cost=Decimal("25.00"),
        )

        self.add_sale_item(
            sale=sale_2,
            quantity=Decimal("4.000"),
            unit_price=Decimal("50.00"),
            unit_cost=Decimal("25.00"),
        )

        result = get_sales_trend(
            interval="month",
        )

        self.assertEqual(len(result), 2)

        self.assertEqual(
            result[0]["date"],
            date(2026, 2, 1),
        )

        self.assertEqual(
            result[0]["transaction_count"],
            1,
        )

        self.assertEqual(
            result[0]["revenue"],
            Decimal("100.00"),
        )

        self.assertEqual(
            result[1]["date"],
            date(2026, 3, 1),
        )

        self.assertEqual(
            result[1]["transaction_count"],
            1,
        )

        self.assertEqual(
            result[1]["revenue"],
            Decimal("200.00"),
        )


    def test_sales_trend_discount_affects_revenue_but_not_gross_sales_value(self):
        sale = self.create_completed_sale(
            reference="SALE-001",
            subtotal_amount=Decimal("100.00"),
            discount_amount=Decimal("20.00"),
            total_amount=Decimal("80.00"),
            completed_at=datetime(
                2026,
                4,
                10,
                10,
                0,
                tzinfo=timezone.utc,
            ),
        )

        self.add_sale_item(
            sale=sale,
            quantity=Decimal("2.000"),
            unit_price=Decimal("50.00"),
            unit_cost=Decimal("25.00"),
        )

        result = get_sales_trend()

        self.assertEqual(len(result), 1)

        self.assertEqual(
            result[0]["gross_sales_value"],
            Decimal("100.00"),
        )

        self.assertEqual(
            result[0]["revenue"],
            Decimal("80.00"),
        )


    def test_sales_trend_multiple_items_do_not_duplicate_revenue(self):
        sale = self.create_completed_sale(
            reference="SALE-001",
            total_amount=Decimal("150.00"),
            completed_at=datetime(
                2026,
                5,
                10,
                10,
                0,
                tzinfo=timezone.utc,
            ),
        )

        self.add_sale_item(
            sale=sale,
            quantity=Decimal("1.000"),
            unit_price=Decimal("100.00"),
            unit_cost=Decimal("50.00"),
        )

        self.add_sale_item(
            sale=sale,
            quantity=Decimal("1.000"),
            unit_price=Decimal("50.00"),
            unit_cost=Decimal("25.00"),
        )

        result = get_sales_trend()

        self.assertEqual(len(result), 1)

        self.assertEqual(
            result[0]["transaction_count"],
            1,
        )

        self.assertEqual(
            result[0]["units_sold"],
            Decimal("2.000"),
        )

        self.assertEqual(
            result[0]["gross_sales_value"],
            Decimal("150.00"),
        )

        # Must remain 150, not 300.
        self.assertEqual(
            result[0]["revenue"],
            Decimal("150.00"),
        )


    def test_sales_trend_excludes_draft_sales(self):
        completed_sale = self.create_completed_sale(
            reference="SALE-001",
            total_amount=Decimal("100.00"),
            completed_at=datetime(
                2026,
                6,
                10,
                10,
                0,
                tzinfo=timezone.utc,
            ),
        )

        draft_sale = Sale.objects.create(
            reference="SALE-002",
            payment_type=Sale.PaymentType.CASH,
            status=Sale.Status.DRAFT,
            subtotal_amount=Decimal("200.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("200.00"),
            created_by=self.user,
            completed_at=datetime(
                2026,
                6,
                10,
                11,
                0,
                tzinfo=timezone.utc,
            ),
        )

        self.add_sale_item(
            sale=completed_sale,
            quantity=Decimal("1.000"),
            unit_price=Decimal("100.00"),
            unit_cost=Decimal("50.00"),
        )

        self.add_sale_item(
            sale=draft_sale,
            quantity=Decimal("2.000"),
            unit_price=Decimal("100.00"),
            unit_cost=Decimal("50.00"),
        )

        result = get_sales_trend()

        self.assertEqual(len(result), 1)

        self.assertEqual(
            result[0]["transaction_count"],
            1,
        )

        self.assertEqual(
            result[0]["units_sold"],
            Decimal("1.000"),
        )

        self.assertEqual(
            result[0]["revenue"],
            Decimal("100.00"),
        )


    def test_sales_trend_excludes_cancelled_sales(self):
        completed_sale = self.create_completed_sale(
            reference="SALE-001",
            total_amount=Decimal("100.00"),
            completed_at=datetime(
                2026,
                7,
                10,
                10,
                0,
                tzinfo=timezone.utc,
            ),
        )

        cancelled_sale = Sale.objects.create(
            reference="SALE-002",
            payment_type=Sale.PaymentType.CASH,
            status=Sale.Status.CANCELLED,
            subtotal_amount=Decimal("200.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("200.00"),
            created_by=self.user,
            completed_at=datetime(
                2026,
                7,
                10,
                11,
                0,
                tzinfo=timezone.utc,
            ),
        )

        self.add_sale_item(
            sale=completed_sale,
            quantity=Decimal("1.000"),
            unit_price=Decimal("100.00"),
            unit_cost=Decimal("50.00"),
        )

        self.add_sale_item(
            sale=cancelled_sale,
            quantity=Decimal("2.000"),
            unit_price=Decimal("100.00"),
            unit_cost=Decimal("50.00"),
        )

        result = get_sales_trend()

        self.assertEqual(len(result), 1)

        self.assertEqual(
            result[0]["transaction_count"],
            1,
        )

        self.assertEqual(
            result[0]["units_sold"],
            Decimal("1.000"),
        )

        self.assertEqual(
            result[0]["revenue"],
            Decimal("100.00"),
        )


    def test_sales_trend_date_range_filters_sales(self):
        sale_before = self.create_completed_sale(
            reference="SALE-001",
            total_amount=Decimal("100.00"),
            completed_at=datetime(
                2026,
                8,
                1,
                10,
                0,
                tzinfo=timezone.utc,
            ),
        )

        sale_inside = self.create_completed_sale(
            reference="SALE-002",
            total_amount=Decimal("200.00"),
            completed_at=datetime(
                2026,
                8,
                10,
                10,
                0,
                tzinfo=timezone.utc,
            ),
        )

        sale_after = self.create_completed_sale(
            reference="SALE-003",
            total_amount=Decimal("300.00"),
            completed_at=datetime(
                2026,
                8,
                20,
                10,
                0,
                tzinfo=timezone.utc,
            ),
        )

        self.add_sale_item(
            sale=sale_before,
            quantity=Decimal("1.000"),
            unit_price=Decimal("100.00"),
            unit_cost=Decimal("50.00"),
        )

        self.add_sale_item(
            sale=sale_inside,
            quantity=Decimal("2.000"),
            unit_price=Decimal("100.00"),
            unit_cost=Decimal("50.00"),
        )

        self.add_sale_item(
            sale=sale_after,
            quantity=Decimal("3.000"),
            unit_price=Decimal("100.00"),
            unit_cost=Decimal("50.00"),
        )

        result = get_sales_trend(
            start_date=date(2026, 8, 5),
            end_date=date(2026, 8, 15),
        )

        self.assertEqual(len(result), 1)

        self.assertEqual(
            result[0]["date"],
            date(2026, 8, 10),
        )

        self.assertEqual(
            result[0]["transaction_count"],
            1,
        )

        self.assertEqual(
            result[0]["units_sold"],
            Decimal("2.000"),
        )

        self.assertEqual(
            result[0]["gross_sales_value"],
            Decimal("200.00"),
        )

        self.assertEqual(
            result[0]["revenue"],
            Decimal("200.00"),
        )

    def test_sales_trend_date_range_uses_store_timezone(self):
        """
        Date filtering must use the configured store timezone.

        With Asia/Damascus:
            2026-01-02 20:30 UTC = 2026-01-02 23:30 local
            2026-01-02 21:30 UTC = 2026-01-03 00:30 local

        A report for January 2 must include the first sale only.
        """
        sale_before_midnight_utc = self.create_completed_sale(
            reference="TZ-001",
            total_amount=Decimal("100.00"),
            completed_at=datetime(
                2026,
                1,
                2,
                20,
                30,
                tzinfo=timezone.utc,
            ),
        )

        sale_after_midnight_utc = self.create_completed_sale(
            reference="TZ-002",
            total_amount=Decimal("200.00"),
            completed_at=datetime(
                2026,
                1,
                2,
                21,
                30,
                tzinfo=timezone.utc,
            ),
        )

        self.add_sale_item(
            sale=sale_before_midnight_utc,
            quantity=Decimal("1.000"),
            unit_price=Decimal("100.00"),
            unit_cost=Decimal("50.00"),
        )

        self.add_sale_item(
            sale=sale_after_midnight_utc,
            quantity=Decimal("2.000"),
            unit_price=Decimal("100.00"),
            unit_cost=Decimal("50.00"),
        )

        result = get_sales_trend(
            start_date=date(2026, 1, 2),
            end_date=date(2026, 1, 2),
            interval="day",
        )

        self.assertEqual(len(result), 1)

        self.assertEqual(
            result[0]["date"],
            date(2026, 1, 2),
        )

        self.assertEqual(
            result[0]["transaction_count"],
            1,
        )

        self.assertEqual(
            result[0]["units_sold"],
            Decimal("1.000"),
        )

        self.assertEqual(
            result[0]["gross_sales_value"],
            Decimal("100.00"),
        )

        self.assertEqual(
            result[0]["revenue"],
            Decimal("100.00"),
        )


    def test_sales_trend_uses_store_timezone_not_activated_timezone(self):
        """
        Analytics must use the configured store timezone even when
        Django has another timezone currently activated.

        The sale occurs at:
            2026-01-02 20:30 UTC
            2026-01-02 23:30 Asia/Damascus

        Therefore it belongs to January 2 in the store timezone.
        """
        sale = self.create_completed_sale(
            reference="TZ-003",
            total_amount=Decimal("100.00"),
            completed_at=datetime(
                2026,
                1,
                2,
                20,
                30,
                tzinfo=timezone.utc,
            ),
        )

        self.add_sale_item(
            sale=sale,
            quantity=Decimal("1.000"),
            unit_price=Decimal("100.00"),
            unit_cost=Decimal("50.00"),
        )

        with django_timezone.override("UTC"):
            result = get_sales_trend(
                start_date=date(2026, 1, 2),
                end_date=date(2026, 1, 2),
                interval="day",
            )

        self.assertEqual(len(result), 1)

        self.assertEqual(
            result[0]["date"],
            date(2026, 1, 2),
        )

        self.assertEqual(
            result[0]["transaction_count"],
            1,
        )

        self.assertEqual(
            result[0]["units_sold"],
            Decimal("1.000"),
        )

        self.assertEqual(
            result[0]["gross_sales_value"],
            Decimal("100.00"),
        )

        self.assertEqual(
            result[0]["revenue"],
            Decimal("100.00"),
        )


    def test_sales_trend_invalid_interval_raises_error(self):
        with self.assertRaises(ValueError):
            get_sales_trend(
                interval="year",
            )

    def test_product_profitability_ranks_by_gross_profit(self):
        """
        Products must be ranked by gross profit descending,
        not by gross sales value.

        Product A:
            Gross sales = 1,000
            COGS        =   900
            Gross profit=   100

        Product B:
            Gross sales =   500
            COGS        =   100
            Gross profit=   400

        Therefore Product B must rank first even though
        Product A has higher gross sales.
        """

        product_a = Product.objects.create(
            name="High Revenue Low Profit",
            category=self.category,
            unit=self.unit,
            current_purchase_cost=Decimal("90.00"),
            current_sell_price=Decimal("100.00"),
            minimum_stock=Decimal("10.00"),
            current_stock=Decimal("20.00"),
        )

        product_b = Product.objects.create(
            name="Lower Revenue High Profit",
            category=self.category,
            unit=self.unit,
            current_purchase_cost=Decimal("20.00"),
            current_sell_price=Decimal("100.00"),
            minimum_stock=Decimal("10.00"),
            current_stock=Decimal("20.00"),
        )

        sale_a = self.create_completed_sale(
            reference="PROFIT-001",
            total_amount=Decimal("1000.00"),
        )

        SaleItem.objects.create(
            sale=sale_a,
            product=product_a,
            quantity=Decimal("10.000"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("1000.00"),
            unit_cost=Decimal("90.00"),
        )

        sale_b = self.create_completed_sale(
            reference="PROFIT-002",
            total_amount=Decimal("500.00"),
        )

        SaleItem.objects.create(
            sale=sale_b,
            product=product_b,
            quantity=Decimal("5.000"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("500.00"),
            unit_cost=Decimal("20.00"),
        )

        result = get_product_profitability(limit=2)

        self.assertEqual(len(result), 2)

        # Product B has lower revenue but higher gross profit,
        # so it must rank first.
        self.assertEqual(
            result[0]["product__name"],
            "Lower Revenue High Profit",
        )
        self.assertEqual(
            result[0]["gross_sales_value"],
            Decimal("500.00"),
        )
        self.assertEqual(
            result[0]["cogs"],
            Decimal("100.00"),
        )
        self.assertEqual(
            result[0]["gross_profit"],
            Decimal("400.00"),
        )
        self.assertEqual(
            result[0]["gross_margin"],
            Decimal("80.00"),
        )

        # Product A has higher revenue but lower gross profit,
        # so it must rank second.
        self.assertEqual(
            result[1]["product__name"],
            "High Revenue Low Profit",
        )
        self.assertEqual(
            result[1]["gross_sales_value"],
            Decimal("1000.00"),
        )
        self.assertEqual(
            result[1]["cogs"],
            Decimal("900.00"),
        )
        self.assertEqual(
            result[1]["gross_profit"],
            Decimal("100.00"),
        )
        self.assertEqual(
            result[1]["gross_margin"],
            Decimal("10.00"),
        )

    def test_product_profitability_limit_applies_after_gross_profit_ranking(self):
        """
        The limit must be applied after products are ranked by gross profit.

        Product A:
            Gross sales = 1,000
            COGS        =   900
            Gross profit=   100

        Product B:
            Gross sales =   500
            COGS        =   100
            Gross profit=   400

        With limit=1, Product B must be returned because it has
        the highest gross profit, even though Product A has
        higher gross sales.
        """

        product_a = Product.objects.create(
            name="High Revenue Low Profit",
            category=self.category,
            unit=self.unit,
            current_purchase_cost=Decimal("90.00"),
            current_sell_price=Decimal("100.00"),
            minimum_stock=Decimal("10.00"),
            current_stock=Decimal("20.00"),
        )

        product_b = Product.objects.create(
            name="Lower Revenue High Profit",
            category=self.category,
            unit=self.unit,
            current_purchase_cost=Decimal("20.00"),
            current_sell_price=Decimal("100.00"),
            minimum_stock=Decimal("10.00"),
            current_stock=Decimal("20.00"),
        )

        sale_a = self.create_completed_sale(
            reference="PROFIT-001",
            total_amount=Decimal("1000.00"),
        )

        SaleItem.objects.create(
            sale=sale_a,
            product=product_a,
            quantity=Decimal("10.000"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("1000.00"),
            unit_cost=Decimal("90.00"),
        )

        sale_b = self.create_completed_sale(
            reference="PROFIT-002",
            total_amount=Decimal("500.00"),
        )

        SaleItem.objects.create(
            sale=sale_b,
            product=product_b,
            quantity=Decimal("5.000"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("500.00"),
            unit_cost=Decimal("20.00"),
        )

        result = get_product_profitability(limit=1)

        self.assertEqual(len(result), 1)

        self.assertEqual(
            result[0]["product__name"],
            "Lower Revenue High Profit",
        )

        self.assertEqual(
            result[0]["gross_sales_value"],
            Decimal("500.00"),
        )

        self.assertEqual(
            result[0]["cogs"],
            Decimal("100.00"),
        )

        self.assertEqual(
            result[0]["gross_profit"],
            Decimal("400.00"),
        )

        self.assertEqual(
            result[0]["gross_margin"],
            Decimal("80.00"),
        )

