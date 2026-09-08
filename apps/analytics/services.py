from decimal import ROUND_HALF_UP, Decimal

from django.db.models import DecimalField, ExpressionWrapper, F, Sum ,Count
from django.db.models.functions import Coalesce

from apps.sales.models import Sale, SaleItem


TWO_PLACES = Decimal("0.01")


def get_profitability_summary(start_date=None, end_date=None):
    """
    Return a profitability summary for completed sales.

    Revenue is based on the final sale total after discounts
    (Sale.total_amount).

    COGS is based on the historical cost snapshots stored on
    completed SaleItem records (quantity * unit_cost), computed
    at query time rather than read from a duplicated stored field.

    Gross Profit:
        Revenue - COGS

    Gross Margin:
        Gross Profit / Revenue * 100
        (0.00 if Revenue is 0, to avoid division by zero)

    Optional date filters are applied to the sale completion date.

    Args:
        start_date: Optional inclusive start date.
        end_date: Optional inclusive end date.

    Returns:
        dict containing:
            revenue
            cogs
            gross_profit
            gross_margin
    """
    completed_sales = Sale.objects.filter(status=Sale.Status.COMPLETED)

    if start_date is not None:
        completed_sales = completed_sales.filter(completed_at__date__gte=start_date)

    if end_date is not None:
        completed_sales = completed_sales.filter(completed_at__date__lte=end_date)

    revenue_agg = completed_sales.aggregate(
        total=Coalesce(Sum("total_amount"), Decimal("0.00"))
    )
    revenue = revenue_agg["total"].quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

    sale_items = SaleItem.objects.filter(sale__in=completed_sales).annotate(
        line_cost=ExpressionWrapper(
            F("quantity") * F("unit_cost"),
            output_field=DecimalField(max_digits=20, decimal_places=5),
        )
    )

    cogs_agg = sale_items.aggregate(
        total=Coalesce(Sum("line_cost"), Decimal("0.00"))
    )
    cogs = cogs_agg["total"].quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

    gross_profit = (revenue - cogs).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

    if revenue > Decimal("0.00"):
        gross_margin = (
            gross_profit / revenue * Decimal("100")
        ).quantize(Decimal("0.01"))
    else:
        gross_margin = None

    return {
        "revenue": revenue,
        "cogs": cogs,
        "gross_profit": gross_profit,
        "gross_margin": gross_margin,
    }

def get_top_selling_products(
    start_date=None,
    end_date=None,
    limit=10,
):
    """
    Return the top-selling products from completed sales.

    Products are ranked by total quantity sold.

    Metrics:
        quantity_sold:
            Total quantity sold.

        sales_count:
            Number of completed sales containing the product.

        gross_sales_value:
            Sum of SaleItem.line_total, representing gross
            sales value before any sale-level discount.

    Optional date filters are applied to the sale completion date.

    Args:
        start_date: Optional inclusive start date.
        end_date: Optional inclusive end date.
        limit: Maximum number of products to return.

    Returns:
        A list of dictionaries ordered by quantity sold descending.
    """
    completed_items = (
        SaleItem.objects
        .filter(
            sale__status=Sale.Status.COMPLETED,
        )
        .select_related("product")
    )

    if start_date is not None:
        completed_items = completed_items.filter(
            sale__completed_at__date__gte=start_date
        )

    if end_date is not None:
        completed_items = completed_items.filter(
            sale__completed_at__date__lte=end_date
        )

    products = (
        completed_items
        .values(
            "product_id",
            "product__name",
        )
        .annotate(
            quantity_sold=Sum("quantity"),
            sales_count=Count("sale_id", distinct=True),
            gross_sales_value=Sum("line_total"),
        )
        .order_by(
            "-quantity_sold",
            "product__name",
        )
    )

    return list(products[:limit])

def get_slow_moving_products(
    start_date=None,
    end_date=None,
    limit=10,
):
    """
    Return the slowest-selling products from completed sales.

    Products are ranked by total quantity sold ascending.

    Metrics:
        quantity_sold:
            Total quantity sold during the selected period.

        sales_count:
            Number of completed sales containing the product.

        gross_sales_value:
            Sum of SaleItem.line_total, representing gross
            sales value before any sale-level discount.

    Optional date filters are applied to the sale completion date.

    Products with no sales are excluded.

    Args:
        start_date: Optional inclusive start date.
        end_date: Optional inclusive end date.
        limit: Maximum number of products to return.

    Returns:
        A list of dictionaries ordered by quantity sold ascending.
    """

    completed_items = (
        SaleItem.objects
        .filter(
            sale__status=Sale.Status.COMPLETED,
        )
    )

    if start_date is not None:
        completed_items = completed_items.filter(
            sale__completed_at__date__gte=start_date
        )

    if end_date is not None:
        completed_items = completed_items.filter(
            sale__completed_at__date__lte=end_date
        )

    products = (
        completed_items
        .values(
            "product_id",
            "product__name",
        )
        .annotate(
            quantity_sold=Sum("quantity"),
            sales_count=Count(
                "sale_id",
                distinct=True,
            ),
            gross_sales_value=Sum("line_total"),
        )
        .order_by(
            "quantity_sold",
            "product__name",
        )
    )

    return list(products[:limit])

def get_product_profitability(
    start_date=None,
    end_date=None,
    limit=10,
):
    """
    Return product-level gross profitability for completed sales.

    Metrics:
        quantity_sold:
            Total quantity sold.

        gross_sales_value:
            Sum of SaleItem.line_total, representing gross
            sales value before sale-level discounts.

        cogs:
            Total cost of goods sold based on historical
            SaleItem.unit_cost snapshots.

        gross_profit:
            Gross sales value minus COGS.

        gross_margin:
            Gross profit divided by gross sales value,
            expressed as a percentage.

    Optional date filters are applied to the sale completion date.

    Products are ranked by gross profit descending.
    """

    completed_items = (
        SaleItem.objects
        .filter(
            sale__status=Sale.Status.COMPLETED,
        )
    )

    if start_date is not None:
        completed_items = completed_items.filter(
            sale__completed_at__date__gte=start_date
        )

    if end_date is not None:
        completed_items = completed_items.filter(
            sale__completed_at__date__lte=end_date
        )

    items_with_cost = completed_items.annotate(
        line_cost=ExpressionWrapper(
            F("quantity") * F("unit_cost"),
            output_field=DecimalField(
                max_digits=20,
                decimal_places=5,
            ),
        )
    )

    products = (
        items_with_cost
        .values(
            "product_id",
            "product__name",
        )
        .annotate(
            quantity_sold=Sum("quantity"),
            gross_sales_value=Sum("line_total"),
            cogs=Sum("line_cost"),
        )
        .order_by(
            "-gross_sales_value",
            "product__name",
        )
    )

    results = []

    for product in products[:limit]:
        gross_sales_value = (
            product["gross_sales_value"]
            or Decimal("0.00")
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        cogs = (
            product["cogs"]
            or Decimal("0.00")
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        gross_profit = (
            gross_sales_value - cogs
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        if gross_sales_value > Decimal("0.00"):
            gross_margin = (
                gross_profit
                / gross_sales_value
                * Decimal("100")
            ).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP,
            )
        else:
            gross_margin = None

        results.append(
            {
                "product_id": product["product_id"],
                "product__name": product["product__name"],
                "quantity_sold": product["quantity_sold"],
                "gross_sales_value": gross_sales_value,
                "cogs": cogs,
                "gross_profit": gross_profit,
                "gross_margin": gross_margin,
            }
        )

    return results