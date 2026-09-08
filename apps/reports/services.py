from decimal import Decimal

from django.db import models
from django.db.models.functions import Coalesce

from apps.customers.models import Customer
from apps.expenses.models import Expense
from apps.payments.models import CustomerPayment, SupplierPayment
from apps.products.models import Product
from apps.purchases.models import Purchase
from apps.sales.models import Sale
from apps.suppliers.models import Supplier
from apps.sales.models import Sale, SaleItem

def get_sales_summary():
    """
    Return a summary of completed sales.

    Draft and cancelled sales are excluded.

    Profitability is calculated from the historical cost snapshots
    stored on completed sale items.
    """

    completed_sales = Sale.objects.filter(
        status=Sale.Status.COMPLETED,
    )

    sales_summary = completed_sales.aggregate(
        sales_count=models.Count("id"),
        total_revenue=models.Sum("total_amount"),

        cash_sales_amount=models.Sum(
            "total_amount",
            filter=models.Q(
                payment_type=Sale.PaymentType.CASH,
            ),
        ),

        credit_sales_amount=models.Sum(
            "total_amount",
            filter=models.Q(
                payment_type=Sale.PaymentType.CREDIT,
            ),
        ),

        cash_sales_count=models.Count(
            "id",
            filter=models.Q(
                payment_type=Sale.PaymentType.CASH,
            ),
        ),

        credit_sales_count=models.Count(
            "id",
            filter=models.Q(
                payment_type=Sale.PaymentType.CREDIT,
            ),
        ),
    )

    total_cogs = (
        SaleItem.objects
        .filter(
            sale__status=Sale.Status.COMPLETED,
        )
        .aggregate(
            total=models.Sum("cost_total"),
        )["total"]
        or Decimal("0.00")
    )

    total_revenue = (
        sales_summary["total_revenue"]
        or Decimal("0.00")
    )

    gross_profit = (
        total_revenue - total_cogs
    ).quantize(Decimal("0.01"))

    if total_revenue > Decimal("0.00"):
        gross_margin = (
            gross_profit / total_revenue * Decimal("100")
        ).quantize(Decimal("0.01"))
    else:
        gross_margin = Decimal("0.00")

    return {
        "sales_count": (
            sales_summary["sales_count"]
            or 0
        ),

        "total_revenue": total_revenue,
        "total_cogs": total_cogs,
        "gross_profit": gross_profit,
        "gross_margin": gross_margin,

        "cash_sales_amount": (
            sales_summary["cash_sales_amount"]
            or Decimal("0.00")
        ),

        "credit_sales_amount": (
            sales_summary["credit_sales_amount"]
            or Decimal("0.00")
        ),

        "cash_sales_count": (
            sales_summary["cash_sales_count"]
            or 0
        ),

        "credit_sales_count": (
            sales_summary["credit_sales_count"]
            or 0
        ),
    }

def get_expense_summary():
    """
    Return a summary of recorded expenses.

    Expenses are summarized by total amount and category.
    """

    summary = Expense.objects.aggregate(
        expense_count=models.Count("id"),
        total_expenses=models.Sum("amount"),
    )

    expenses_by_category = (
        Expense.objects
        .values("category")
        .annotate(
            total=models.Sum("amount"),
        )
        .order_by("-total")
    )

    return {
        "expense_count": summary["expense_count"] or 0,
        "total_expenses": summary["total_expenses"] or Decimal("0.00"),
        "by_category": list(expenses_by_category),
    }


def get_inventory_report():
    """
    Return the current inventory status for all products.
    """

    return (
        Product.objects
        .select_related("unit", "category")
        .values(
            "id",
            "name",
            "current_stock",
            "minimum_stock",
            "unit__name",
            "unit__symbol",
            "current_purchase_cost",
            "current_sell_price",
        )
        .order_by("name")
    )


def get_low_stock_report():
    """
    Return active products whose current stock is at or below
    their configured minimum stock level.
    """

    return (
        Product.objects
        .select_related("unit", "category")
        .filter(
            current_stock__lte=models.F("minimum_stock"),
            is_active=True,
        )
        .values(
            "id",
            "name",
            "current_stock",
            "minimum_stock",
            "unit__name",
            "unit__symbol",
        )
        .order_by("current_stock", "name")
    )


def get_customer_debt_report():
    """
    Return customers with outstanding debt.

    Outstanding debt is calculated as:

        Completed Credit Sales - Customer Payments

    Only customers with a positive outstanding balance are returned.
    """

    credit_sales = (
        Sale.objects
        .filter(
            customer=models.OuterRef("pk"),
            payment_type=Sale.PaymentType.CREDIT,
            status=Sale.Status.COMPLETED,
        )
        .values("customer")
        .annotate(
            total=models.Sum("total_amount"),
        )
        .values("total")
    )

    customer_payments = (
        CustomerPayment.objects
        .filter(
            customer=models.OuterRef("pk"),
        )
        .values("customer")
        .annotate(
            total=models.Sum("amount"),
        )
        .values("total")
    )

    customers = (
        Customer.objects
        .annotate(
            credit_sales_total=Coalesce(
                models.Subquery(
                    credit_sales,
                    output_field=models.DecimalField(
                        max_digits=14,
                        decimal_places=2,
                    ),
                ),
                Decimal("0.00"),
            ),
            payments_total=Coalesce(
                models.Subquery(
                    customer_payments,
                    output_field=models.DecimalField(
                        max_digits=14,
                        decimal_places=2,
                    ),
                ),
                Decimal("0.00"),
            ),
        )
        .annotate(
            outstanding_balance=(
                models.F("credit_sales_total")
                - models.F("payments_total")
            ),
        )
        .filter(
            outstanding_balance__gt=Decimal("0.00"),
        )
        .values(
            "id",
            "name",
            "credit_sales_total",
            "payments_total",
            "outstanding_balance",
        )
        .order_by("-outstanding_balance", "name")
    )

    return customers

def get_supplier_balance_report():
    """
    Return suppliers with outstanding balances.

    Outstanding balance is calculated as:

        Completed Credit Purchases - Supplier Payments

    Only suppliers with a positive outstanding balance are returned.
    """

    credit_purchases = (
        Purchase.objects
        .filter(
            supplier=models.OuterRef("pk"),
            payment_type=Purchase.PaymentType.CREDIT,
            status=Purchase.Status.COMPLETED,
        )
        .values("supplier")
        .annotate(
            total=models.Sum("total_amount"),
        )
        .values("total")
    )

    supplier_payments = (
        SupplierPayment.objects
        .filter(
            supplier=models.OuterRef("pk"),
        )
        .values("supplier")
        .annotate(
            total=models.Sum("amount"),
        )
        .values("total")
    )

    suppliers = (
        Supplier.objects
        .annotate(
            credit_purchases_total=Coalesce(
                models.Subquery(
                    credit_purchases,
                    output_field=models.DecimalField(
                        max_digits=14,
                        decimal_places=2,
                    ),
                ),
                Decimal("0.00"),
            ),
            payments_total=Coalesce(
                models.Subquery(
                    supplier_payments,
                    output_field=models.DecimalField(
                        max_digits=14,
                        decimal_places=2,
                    ),
                ),
                Decimal("0.00"),
            ),
        )
        .annotate(
            outstanding_balance=(
                models.F("credit_purchases_total")
                - models.F("payments_total")
            ),
        )
        .filter(
            outstanding_balance__gt=Decimal("0.00"),
        )
        .values(
            "id",
            "name",
            "credit_purchases_total",
            "payments_total",
            "outstanding_balance",
        )
        .order_by("-outstanding_balance", "name")
    )

    return suppliers