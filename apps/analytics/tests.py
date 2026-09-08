from datetime import date, datetime, time, timezone
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.products.models import Category, Product, Unit
from apps.analytics.services import get_profitability_summary
from apps.sales.models import Sale, SaleItem

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

        cost_total = (
            quantity * unit_cost
        ).quantize(Decimal("0.01"))

        return SaleItem.objects.create(
            sale=sale,
            product=self.product,
            quantity=quantity,
            unit_price=unit_price,
            line_total=line_total,
            unit_cost=unit_cost,
            cost_total=cost_total,
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

