from datetime import datetime, time, timedelta
from decimal import ROUND_HALF_UP, Decimal

from django.db.models import (
    Count,
    DecimalField,
    ExpressionWrapper,
    F,
    Sum,
)
from django.db.models.functions import (
    Coalesce,
    TruncDay,
    TruncMonth,
    TruncWeek,
)
from django.utils import timezone as django_timezone

from apps.sales.models import Sale, SaleItem

TWO_PLACES = Decimal("0.01")


def _date_range_bounds(start_date, end_date, store_timezone):
    """
    Build explicit, store-timezone-aware datetime bounds for a
    [start_date, end_date] inclusive date range, expressed as a
    half-open interval:

        [start_date 00:00:00, end_date + 1 day 00:00:00)

    Both start_dt and end_dt are computed against the store's fixed
    timezone (settings.TIME_ZONE) rather than whatever timezone is
    currently activated on the request/thread, so that the same
    start_date/end_date arguments always mean the same actual instants
    regardless of who calls this or from what context.

    The upper bound is deliberately half-open (__lt on end_date + 1
    day) rather than closed (__lte on end_date at 23:59:59.999999).
    A closed bound approximated with time.max can miss a sale whose
    timestamp carries precision beyond what time.max represents,
    silently excluding it from the range.

    Returns a (start_dt, end_dt) tuple; either element is None if the
    corresponding argument was None.
    """
    start_dt = None
    end_dt = None

    if start_date is not None:
        start_dt = django_timezone.make_aware(
            datetime.combine(start_date, time.min),
            store_timezone,
        )

    if end_date is not None:
        end_dt = django_timezone.make_aware(
            datetime.combine(end_date + timedelta(days=1), time.min),
            store_timezone,
        )

    return start_dt, end_dt


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
        (None if Revenue is 0, since margin is undefined when
        there's no revenue to divide by)

    Optional date filters are applied to the sale completion date,
    using the store's fixed timezone and a half-open date interval.
    See _date_range_bounds for details. This matches the boundary
    handling used by every other function in this module, so the
    same start_date/end_date arguments include the same set of sales
    everywhere.

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
    store_timezone = django_timezone.get_default_timezone()
    start_dt, end_dt = _date_range_bounds(start_date, end_date, store_timezone)

    completed_sales = Sale.objects.filter(status=Sale.Status.COMPLETED)

    if start_dt is not None:
        completed_sales = completed_sales.filter(completed_at__gte=start_dt)

    if end_dt is not None:
        completed_sales = completed_sales.filter(completed_at__lt=end_dt)

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
        ).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
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

    Optional date filters are applied to the sale completion date,
    using the store's fixed timezone and a half-open date interval.
    See _date_range_bounds for details.

    Args:
        start_date: Optional inclusive start date.
        end_date: Optional inclusive end date.
        limit: Maximum number of products to return.

    Returns:
        A list of dictionaries ordered by quantity sold descending.
    """
    store_timezone = django_timezone.get_default_timezone()
    start_dt, end_dt = _date_range_bounds(start_date, end_date, store_timezone)

    completed_items = SaleItem.objects.filter(
        sale__status=Sale.Status.COMPLETED,
    )

    if start_dt is not None:
        completed_items = completed_items.filter(
            sale__completed_at__gte=start_dt,
        )

    if end_dt is not None:
        completed_items = completed_items.filter(
            sale__completed_at__lt=end_dt,
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

    Optional date filters are applied to the sale completion date,
    using the store's fixed timezone and a half-open date interval.
    See _date_range_bounds for details.

    Products with no sales are excluded.

    Args:
        start_date: Optional inclusive start date.
        end_date: Optional inclusive end date.
        limit: Maximum number of products to return.

    Returns:
        A list of dictionaries ordered by quantity sold ascending.
    """
    store_timezone = django_timezone.get_default_timezone()
    start_dt, end_dt = _date_range_bounds(start_date, end_date, store_timezone)

    completed_items = SaleItem.objects.filter(
        sale__status=Sale.Status.COMPLETED,
    )

    if start_dt is not None:
        completed_items = completed_items.filter(
            sale__completed_at__gte=start_dt,
        )

    if end_dt is not None:
        completed_items = completed_items.filter(
            sale__completed_at__lt=end_dt,
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

    Optional date filters are applied to the sale completion date,
    using the store's fixed timezone and a half-open date interval.
    See _date_range_bounds for details.

    Products are ranked by gross profit descending.
    """
    store_timezone = django_timezone.get_default_timezone()
    start_dt, end_dt = _date_range_bounds(start_date, end_date, store_timezone)

    completed_items = SaleItem.objects.filter(
        sale__status=Sale.Status.COMPLETED,
    )

    if start_dt is not None:
        completed_items = completed_items.filter(
            sale__completed_at__gte=start_dt,
        )

    if end_dt is not None:
        completed_items = completed_items.filter(
            sale__completed_at__lt=end_dt,
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
        .annotate(
            # Computed from the two aggregates above so ordering (and
            # the [:limit] slice below) actually reflects gross
            # profit, not gross sales value.
            gross_profit_for_ordering=F("gross_sales_value") - F("cogs"),
        )
        .order_by(
            "-gross_profit_for_ordering",
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


def get_sales_trend(
    start_date=None,
    end_date=None,
    interval="day",
):
    """
    Return sales performance aggregated by day, week, or month.

    Metrics:
    - transaction_count: number of completed sales.
    - units_sold: total quantity sold.
    - gross_sales_value: sum of SaleItem.line_total before discounts.
    - revenue: sum of Sale.total_amount after discounts.

    Only completed sales are included.

    Weekly periods start on Monday.
    Monthly periods use the first day of the month.

    The store's default timezone (settings.TIME_ZONE) is used
    explicitly and consistently for BOTH date-range filtering and
    period truncation, so that:

      - reporting periods are deterministic regardless of the
        timezone activated by the current request or execution
        context (e.g. per-user locale settings, or no timezone
        activated at all in a shell/Celery context), and

      - a sale is never included/excluded by the date filter based
        on one timezone interpretation while being grouped into a
        bucket based on a different one. Filtering and truncation
        must agree on the same fixed timezone end-to-end, or a sale
        near a day/week/month boundary in store-local time could be
        filtered using one cutoff and truncated using another.

    Optional date filters use a half-open interval
    [start_date 00:00:00, end_date + 1 day 00:00:00). See
    _date_range_bounds for details.

    Sale-level and item-level metrics are aggregated separately
    to prevent revenue duplication when a sale contains multiple items.
    """

    trunc_functions = {
        "day": TruncDay,
        "week": TruncWeek,
        "month": TruncMonth,
    }

    if interval not in trunc_functions:
        raise ValueError(
            "interval must be one of: day, week, month."
        )

    trunc_function = trunc_functions[interval]

    # Analytics use the store's configured business timezone,
    # not a request/user-specific activated timezone.
    store_timezone = django_timezone.get_default_timezone()
    start_dt, end_dt = _date_range_bounds(start_date, end_date, store_timezone)

    completed_sales = Sale.objects.filter(
        status=Sale.Status.COMPLETED,
    )

    if start_dt is not None:
        completed_sales = completed_sales.filter(
            completed_at__gte=start_dt,
        )

    if end_dt is not None:
        completed_sales = completed_sales.filter(
            completed_at__lt=end_dt,
        )

    # Aggregate sale-level metrics separately.
    sale_trends = (
        completed_sales
        .annotate(
            period=trunc_function(
                "completed_at",
                tzinfo=store_timezone,
            )
        )
        .values("period")
        .annotate(
            transaction_count=Count("id"),
            revenue=Coalesce(
                Sum("total_amount"),
                Decimal("0.00"),
            ),
        )
        .order_by("period")
    )

    # Aggregate item-level metrics separately.
    #
    # This prevents a sale's total_amount from being duplicated
    # when the sale contains multiple SaleItems.
    item_trends = (
        SaleItem.objects
        .filter(
            sale__status=Sale.Status.COMPLETED,
            sale__in=completed_sales,
        )
        .annotate(
            period=trunc_function(
                "sale__completed_at",
                tzinfo=store_timezone,
            )
        )
        .values("period")
        .annotate(
            units_sold=Coalesce(
                Sum("quantity"),
                Decimal("0.000"),
            ),
            gross_sales_value=Coalesce(
                Sum("line_total"),
                Decimal("0.00"),
            ),
        )
        .order_by("period")
    )

    sales_by_period = {
        row["period"]: row
        for row in sale_trends
    }

    items_by_period = {
        row["period"]: row
        for row in item_trends
    }

    periods = sorted(
        set(sales_by_period) | set(items_by_period)
    )

    results = []

    for period in periods:
        sale_data = sales_by_period.get(period, {})
        item_data = items_by_period.get(period, {})

        revenue = (
            sale_data.get("revenue")
            or Decimal("0.00")
        ).quantize(
            TWO_PLACES,
            rounding=ROUND_HALF_UP,
        )

        gross_sales_value = (
            item_data.get("gross_sales_value")
            or Decimal("0.00")
        ).quantize(
            TWO_PLACES,
            rounding=ROUND_HALF_UP,
        )

        results.append(
            {
                "date": period.date(),
                "transaction_count": (
                    sale_data.get("transaction_count")
                    or 0
                ),
                "units_sold": (
                    item_data.get("units_sold")
                    or Decimal("0.000")
                ),
                "gross_sales_value": gross_sales_value,
                "revenue": revenue,
            }
        )

    return results