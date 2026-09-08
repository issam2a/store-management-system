from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.customers.models import Customer
from apps.expenses.models import Expense
from apps.payments.models import CustomerPayment, SupplierPayment
from apps.products.models import Category, Product, Unit
from apps.purchases.models import Purchase
from apps.reports.services import (
get_customer_debt_report,
get_expense_summary,
get_inventory_report,
get_low_stock_report,
get_sales_summary,
get_supplier_balance_report,
)
from apps.sales.models import Sale, SaleItem
from apps.suppliers.models import Supplier

User = get_user_model()

class ReportsTestCase(TestCase):


    def setUp(self):
        self.user = User.objects.create_user(
            username="report_test_user",
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

        self.customer = Customer.objects.create(
            name="Test Customer",
            account_status="ACTIVE",
        )

        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            phone="123456789",
            contact_information="Test supplier",
        )

    # ---------------------------------------------------------
    # Sales Summary
    # ---------------------------------------------------------

    def test_sales_summary_includes_only_completed_sales(self):
        completed_sale = Sale.objects.create(
            reference="SALE-001",
            payment_type=Sale.PaymentType.CASH,
            status=Sale.Status.COMPLETED,
            subtotal_amount=Decimal("100.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("100.00"),
            created_by=self.user,
        )

        SaleItem.objects.create(
            sale=completed_sale,
            product=self.product,
            quantity=Decimal("1.00"),
            unit_price=Decimal("100.00"),
            line_total=Decimal("100.00"),
            unit_cost=Decimal("50.00"),
            cost_total=Decimal("50.00"),
        )

        Sale.objects.create(
            reference="SALE-002",
            payment_type=Sale.PaymentType.CASH,
            status=Sale.Status.DRAFT,
            subtotal_amount=Decimal("200.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("200.00"),
            created_by=self.user,
        )

        Sale.objects.create(
            reference="SALE-003",
            payment_type=Sale.PaymentType.CASH,
            status=Sale.Status.CANCELLED,
            subtotal_amount=Decimal("300.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("300.00"),
            created_by=self.user,
        )

        summary = get_sales_summary()

        self.assertEqual(summary["sales_count"], 1)
        self.assertEqual(
            summary["total_revenue"],
            Decimal("100.00"),
        )
        self.assertEqual(
            summary["total_cogs"],
            Decimal("50.00"),
        )
        self.assertEqual(
            summary["gross_profit"],
            Decimal("50.00"),
        )
        self.assertEqual(
            summary["gross_margin"],
            Decimal("50.00"),
        )

    def test_sales_summary_separates_cash_and_credit_sales(self):
        Sale.objects.create(
            reference="SALE-004",
            payment_type=Sale.PaymentType.CASH,
            status=Sale.Status.COMPLETED,
            subtotal_amount=Decimal("100.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("100.00"),
            created_by=self.user,
        )

        Sale.objects.create(
            reference="SALE-005",
            customer=self.customer,
            payment_type=Sale.PaymentType.CREDIT,
            status=Sale.Status.COMPLETED,
            subtotal_amount=Decimal("250.00"),
            discount_amount=Decimal("50.00"),
            total_amount=Decimal("200.00"),
            created_by=self.user,
        )

        summary = get_sales_summary()

        self.assertEqual(summary["sales_count"], 2)

        self.assertEqual(
            summary["cash_sales_amount"],
            Decimal("100.00"),
        )

        self.assertEqual(
            summary["credit_sales_amount"],
            Decimal("200.00"),
        )

        self.assertEqual(summary["cash_sales_count"], 1)
        self.assertEqual(summary["credit_sales_count"], 1)

    def test_sales_summary_returns_zero_when_no_sales_exist(self):
        summary = get_sales_summary()

        self.assertEqual(summary["sales_count"], 0)

        self.assertEqual(
            summary["total_revenue"],
            Decimal("0.00"),
        )

        self.assertEqual(
            summary["total_cogs"],
            Decimal("0.00"),
        )

        self.assertEqual(
            summary["gross_profit"],
            Decimal("0.00"),
        )

        self.assertEqual(
            summary["gross_margin"],
            Decimal("0.00"),
        )

        self.assertEqual(
            summary["cash_sales_amount"],
            Decimal("0.00"),
        )

        self.assertEqual(
            summary["credit_sales_amount"],
            Decimal("0.00"),
        )

        self.assertEqual(summary["cash_sales_count"], 0)
        self.assertEqual(summary["credit_sales_count"], 0)

    def test_sales_summary_calculates_profitability_from_sale_item_costs(self):
        sale = Sale.objects.create(
            reference="SALE-PROFIT-001",
            payment_type=Sale.PaymentType.CASH,
            status=Sale.Status.COMPLETED,
            subtotal_amount=Decimal("1200.00"),
            discount_amount=Decimal("200.00"),
            total_amount=Decimal("1000.00"),
            created_by=self.user,
        )

        SaleItem.objects.create(
            sale=sale,
            product=self.product,
            quantity=Decimal("4.00"),
            unit_price=Decimal("150.00"),
            line_total=Decimal("600.00"),
            unit_cost=Decimal("50.00"),
            cost_total=Decimal("200.00"),
        )

        SaleItem.objects.create(
            sale=sale,
            product=self.product,
            quantity=Decimal("2.00"),
            unit_price=Decimal("300.00"),
            line_total=Decimal("600.00"),
            unit_cost=Decimal("200.00"),
            cost_total=Decimal("400.00"),
        )

        summary = get_sales_summary()

        self.assertEqual(
            summary["sales_count"],
            1,
        )

        self.assertEqual(
            summary["total_revenue"],
            Decimal("1000.00"),
        )

        self.assertEqual(
            summary["total_cogs"],
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
    # Expense Summary
    # ---------------------------------------------------------

    def test_expense_summary_calculates_total_and_categories(self):
        Expense.objects.create(
            reference="EXP-001",
            category="Rent",
            amount=Decimal("500.00"),
            payment_method="Cash",
            expense_date=date(2026, 9, 1),
            created_by=self.user,
        )

        Expense.objects.create(
            reference="EXP-002",
            category="Rent",
            amount=Decimal("300.00"),
            payment_method="Cash",
            expense_date=date(2026, 9, 2),
            created_by=self.user,
        )

        Expense.objects.create(
            reference="EXP-003",
            category="Electricity",
            amount=Decimal("200.00"),
            payment_method="Cash",
            expense_date=date(2026, 9, 3),
            created_by=self.user,
        )

        summary = get_expense_summary()

        self.assertEqual(summary["expense_count"], 3)

        self.assertEqual(
            summary["total_expenses"],
            Decimal("1000.00"),
        )

        categories = {
            item["category"]: item["total"]
            for item in summary["by_category"]
        }

        self.assertEqual(
            categories["Rent"],
            Decimal("800.00"),
        )

        self.assertEqual(
            categories["Electricity"],
            Decimal("200.00"),
        )

    def test_expense_summary_returns_zero_when_no_expenses_exist(self):
        summary = get_expense_summary()

        self.assertEqual(summary["expense_count"], 0)

        self.assertEqual(
            summary["total_expenses"],
            Decimal("0.00"),
        )

        self.assertEqual(
            summary["by_category"],
            [],
        )

    # ---------------------------------------------------------
    # Inventory Report
    # ---------------------------------------------------------

    def test_inventory_report_returns_product_stock_information(self):
        report = list(get_inventory_report())

        self.assertEqual(len(report), 1)

        product = report[0]

        self.assertEqual(
            product["name"],
            "Test Product",
        )

        self.assertEqual(
            product["current_stock"],
            Decimal("20.00"),
        )

        self.assertEqual(
            product["minimum_stock"],
            Decimal("10.00"),
        )

        self.assertEqual(
            product["current_purchase_cost"],
            Decimal("50.00"),
        )

        self.assertEqual(
            product["current_sell_price"],
            Decimal("100.00"),
        )

    # ---------------------------------------------------------
    # Low Stock Report
    # ---------------------------------------------------------

    def test_low_stock_report_returns_products_at_or_below_minimum(self):
        self.product.current_stock = Decimal("10.00")
        self.product.save()

        report = list(get_low_stock_report())

        self.assertEqual(len(report), 1)

        self.assertEqual(
            report[0]["name"],
            "Test Product",
        )

    def test_low_stock_report_excludes_products_above_minimum(self):
        report = list(get_low_stock_report())

        self.assertEqual(len(report), 0)

    def test_low_stock_report_excludes_inactive_products(self):
        self.product.current_stock = Decimal("5.00")
        self.product.is_active = False
        self.product.save()

        report = list(get_low_stock_report())

        self.assertEqual(len(report), 0)

    # ---------------------------------------------------------
    # Customer Debt Report
    # ---------------------------------------------------------

    def test_customer_debt_report_calculates_outstanding_balance(self):
        Sale.objects.create(
            reference="SALE-DEBT-001",
            customer=self.customer,
            payment_type=Sale.PaymentType.CREDIT,
            status=Sale.Status.COMPLETED,
            subtotal_amount=Decimal("1000.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("1000.00"),
            created_by=self.user,
        )

        CustomerPayment.objects.create(
            reference="CP-001",
            customer=self.customer,
            amount=Decimal("300.00"),
            payment_method="Cash",
            payment_date=date(2026, 9, 5),
            recorded_by=self.user,
        )

        report = list(get_customer_debt_report())

        self.assertEqual(len(report), 1)

        customer = report[0]

        self.assertEqual(
            customer["credit_sales_total"],
            Decimal("1000.00"),
        )

        self.assertEqual(
            customer["payments_total"],
            Decimal("300.00"),
        )

        self.assertEqual(
            customer["outstanding_balance"],
            Decimal("700.00"),
        )

    def test_customer_debt_report_excludes_fully_paid_customer(self):
        Sale.objects.create(
            reference="SALE-DEBT-002",
            customer=self.customer,
            payment_type=Sale.PaymentType.CREDIT,
            status=Sale.Status.COMPLETED,
            subtotal_amount=Decimal("500.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("500.00"),
            created_by=self.user,
        )

        CustomerPayment.objects.create(
            reference="CP-002",
            customer=self.customer,
            amount=Decimal("500.00"),
            payment_method="Cash",
            payment_date=date(2026, 9, 5),
            recorded_by=self.user,
        )

        report = list(get_customer_debt_report())

        self.assertEqual(len(report), 0)

    def test_customer_debt_report_excludes_cash_sales(self):
        Sale.objects.create(
            reference="SALE-CASH-001",
            customer=self.customer,
            payment_type=Sale.PaymentType.CASH,
            status=Sale.Status.COMPLETED,
            subtotal_amount=Decimal("500.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("500.00"),
            created_by=self.user,
        )

        report = list(get_customer_debt_report())

        self.assertEqual(len(report), 0)

    def test_customer_debt_report_excludes_draft_and_cancelled_sales(self):
        Sale.objects.create(
            reference="SALE-DRAFT-001",
            customer=self.customer,
            payment_type=Sale.PaymentType.CREDIT,
            status=Sale.Status.DRAFT,
            subtotal_amount=Decimal("500.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("500.00"),
            created_by=self.user,
        )

        Sale.objects.create(
            reference="SALE-CANCEL-001",
            customer=self.customer,
            payment_type=Sale.PaymentType.CREDIT,
            status=Sale.Status.CANCELLED,
            subtotal_amount=Decimal("700.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("700.00"),
            created_by=self.user,
        )

        report = list(get_customer_debt_report())

        self.assertEqual(len(report), 0)

    # ---------------------------------------------------------
    # Supplier Balance Report
    # ---------------------------------------------------------

    def test_supplier_balance_report_calculates_outstanding_balance(self):
        Purchase.objects.create(
            reference="PUR-001",
            supplier=self.supplier,
            payment_type=Purchase.PaymentType.CREDIT,
            status=Purchase.Status.COMPLETED,
            total_amount=Decimal("2000.00"),
            created_by=self.user,
        )

        SupplierPayment.objects.create(
            reference="SP-001",
            supplier=self.supplier,
            amount=Decimal("750.00"),
            payment_method="Cash",
            payment_date=date(2026, 9, 5),
            recorded_by=self.user,
        )

        report = list(get_supplier_balance_report())

        self.assertEqual(len(report), 1)

        supplier = report[0]

        self.assertEqual(
            supplier["credit_purchases_total"],
            Decimal("2000.00"),
        )

        self.assertEqual(
            supplier["payments_total"],
            Decimal("750.00"),
        )

        self.assertEqual(
            supplier["outstanding_balance"],
            Decimal("1250.00"),
        )

    def test_supplier_balance_report_excludes_fully_paid_supplier(self):
        Purchase.objects.create(
            reference="PUR-002",
            supplier=self.supplier,
            payment_type=Purchase.PaymentType.CREDIT,
            status=Purchase.Status.COMPLETED,
            total_amount=Decimal("1000.00"),
            created_by=self.user,
        )

        SupplierPayment.objects.create(
            reference="SP-002",
            supplier=self.supplier,
            amount=Decimal("1000.00"),
            payment_method="Cash",
            payment_date=date(2026, 9, 5),
            recorded_by=self.user,
        )

        report = list(get_supplier_balance_report())

        self.assertEqual(len(report), 0)

    def test_supplier_balance_report_excludes_cash_purchases(self):
        Purchase.objects.create(
            reference="PUR-CASH-001",
            supplier=self.supplier,
            payment_type=Purchase.PaymentType.CASH,
            status=Purchase.Status.COMPLETED,
            total_amount=Decimal("1000.00"),
            created_by=self.user,
        )

        report = list(get_supplier_balance_report())

        self.assertEqual(len(report), 0)

    def test_supplier_balance_report_excludes_draft_and_cancelled_purchases(self):
        Purchase.objects.create(
            reference="PUR-DRAFT-001",
            supplier=self.supplier,
            payment_type=Purchase.PaymentType.CREDIT,
            status=Purchase.Status.DRAFT,
            total_amount=Decimal("500.00"),
            created_by=self.user,
        )

        Purchase.objects.create(
            reference="PUR-CANCEL-001",
            supplier=self.supplier,
            payment_type=Purchase.PaymentType.CREDIT,
            status=Purchase.Status.CANCELLED,
            total_amount=Decimal("700.00"),
            created_by=self.user,
        )

        report = list(get_supplier_balance_report())

        self.assertEqual(len(report), 0)
