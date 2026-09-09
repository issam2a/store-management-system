from datetime import datetime, time, timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.db.models import (
    Avg,
    Count,
    DecimalField,
    ExpressionWrapper,
    F,
    Max,
    Min,
    Sum,
)
from django.db.models.functions import (
    Coalesce,
    TruncDay,
    TruncMonth,
    TruncWeek,
)
from django.utils import timezone as django_timezone

from apps.products.models import Product
from apps.sales.models import Sale, SaleItem
from apps.payments.models import SupplierPayment
from apps.purchases.models import Purchase, PurchaseItem
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

def get_category_profitability(
    start_date=None,
    end_date=None,
    limit=10,
):
    """
    Return category-level gross profitability for completed sales.

    Metrics:
        quantity_sold:
            Total quantity sold across products in the category.

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

    Categories are ranked by gross profit descending.

    Categories with no completed sales are excluded.
    """

    store_timezone = django_timezone.get_default_timezone()

    start_dt, end_dt = _date_range_bounds(
        start_date,
        end_date,
        store_timezone,
    )

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

    categories = (
        items_with_cost
        .values(
            "product__category_id",
            "product__category__name",
        )
        .annotate(
            quantity_sold=Sum("quantity"),
            gross_sales_value=Sum("line_total"),
            cogs=Sum("line_cost"),
        )
        .annotate(
            gross_profit_for_ordering=(
                F("gross_sales_value") - F("cogs")
            ),
        )
        .order_by(
            "-gross_profit_for_ordering",
            "product__category__name",
        )
    )

    results = []

    for category in categories[:limit]:
        gross_sales_value = (
            category["gross_sales_value"]
            or Decimal("0.00")
        ).quantize(
            TWO_PLACES,
            rounding=ROUND_HALF_UP,
        )

        cogs = (
            category["cogs"]
            or Decimal("0.00")
        ).quantize(
            TWO_PLACES,
            rounding=ROUND_HALF_UP,
        )

        gross_profit = (
            gross_sales_value - cogs
        ).quantize(
            TWO_PLACES,
            rounding=ROUND_HALF_UP,
        )

        if gross_sales_value > Decimal("0.00"):
            gross_margin = (
                gross_profit
                / gross_sales_value
                * Decimal("100")
            ).quantize(
                TWO_PLACES,
                rounding=ROUND_HALF_UP,
            )
        else:
            gross_margin = None

        results.append(
            {
                "product__category_id": (
                    category["product__category_id"]
                ),
                "product__category__name": (
                    category["product__category__name"]
                ),
                "quantity_sold": category["quantity_sold"],
                "gross_sales_value": gross_sales_value,
                "cogs": cogs,
                "gross_profit": gross_profit,
                "gross_margin": gross_margin,
            }
        )

    return results

def get_inventory_performance(
    start_date=None,
    end_date=None,
    limit=10,
):
    """
    Return product-level inventory performance.

    Metrics:
        current_stock:
            Current operational inventory quantity.

        minimum_stock:
            Configured minimum stock level.

        quantity_sold:
            Total quantity sold during the selected period.

        sales_count:
            Number of distinct completed sales containing the product.

        gross_sales_value:
            Gross sales value from completed sale items.

        stock_status:
            OUT_OF_STOCK when current stock is zero.
            LOW_STOCK when current stock is below minimum stock.
            NORMAL otherwise.

    Optional date filters are applied to the sale completion date,
    using the store's fixed timezone and a half-open date interval.

    All active and inactive products are included, including products
    with no completed sales.

    Products are ranked by quantity sold descending, then by
    product name.

    Args:
        start_date: Optional inclusive start date.
        end_date: Optional inclusive end date.
        limit: Maximum number of products to return.

    Returns:
        A list of dictionaries ordered by inventory activity.
    """

    store_timezone = django_timezone.get_default_timezone()

    start_dt, end_dt = _date_range_bounds(
        start_date,
        end_date,
        store_timezone,
    )

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

    sales_by_product = (
        completed_items
        .values("product_id")
        .annotate(
            quantity_sold=Coalesce(
                Sum("quantity"),
                Decimal("0.000"),
            ),
            sales_count=Count(
                "sale_id",
                distinct=True,
            ),
            gross_sales_value=Coalesce(
                Sum("line_total"),
                Decimal("0.00"),
            ),
        )
    )

    sales_by_product = {
        row["product_id"]: row
        for row in sales_by_product
    }

    products = Product.objects.all()

    results = []

    for product in products:
        sales = sales_by_product.get(product.id)

        quantity_sold = (
            sales["quantity_sold"]
            if sales is not None
            else Decimal("0.000")
        )

        sales_count = (
            sales["sales_count"]
            if sales is not None
            else 0
        )

        gross_sales_value = (
            sales["gross_sales_value"]
            if sales is not None
            else Decimal("0.00")
        ).quantize(
            TWO_PLACES,
            rounding=ROUND_HALF_UP,
        )

        if product.current_stock <= Decimal("0.000"):
            stock_status = "OUT_OF_STOCK"
        elif product.current_stock < product.minimum_stock:
            stock_status = "LOW_STOCK"
        else:
            stock_status = "NORMAL"

        results.append(
            {
                "product_id": product.id,
                "product__name": product.name,
                "current_stock": product.current_stock,
                "minimum_stock": product.minimum_stock,
                "quantity_sold": quantity_sold,
                "sales_count": sales_count,
                "gross_sales_value": gross_sales_value,
                "stock_status": stock_status,
            }
        )

    results.sort(
    key=lambda item: (
        -item["quantity_sold"],
        item["product__name"],
        )
    )

    return results[:limit]

def get_supplier_analysis(
    start_date=None,
    end_date=None,
    limit=10,
):
    """
    Return supplier-level purchasing performance.

    Metrics:

        purchase_count:
            Number of completed purchases from the supplier.

        total_purchase_value:
            Total value of completed purchases.

        paid_amount:
            Total supplier payments recorded for the supplier.

        outstanding_balance:
            Current outstanding supplier balance calculated as:

                completed purchases - supplier payments

    Date filters are applied to completed purchase activity using
    the purchase completion date and the store's fixed timezone.

    Supplier payments are not date-filtered because paid_amount and
    outstanding_balance represent the supplier's current financial
    position.

    Draft and cancelled purchases are excluded.

    Suppliers are ranked by total purchase value descending,
    then by supplier name.

    Suppliers with no completed purchases are excluded.
    """

  

    store_timezone = django_timezone.get_default_timezone()

    start_dt, end_dt = _date_range_bounds(
        start_date,
        end_date,
        store_timezone,
    )

    completed_purchases = Purchase.objects.filter(
        status=Purchase.Status.COMPLETED,
    )

    if start_dt is not None:
        completed_purchases = completed_purchases.filter(
            completed_at__gte=start_dt,
        )

    if end_dt is not None:
        completed_purchases = completed_purchases.filter(
            completed_at__lt=end_dt,
        )

    purchase_data = (
        completed_purchases
        .values(
            "supplier_id",
            "supplier__name",
        )
        .annotate(
            purchase_count=Count("id"),
            total_purchase_value=Coalesce(
                Sum("total_amount"),
                Decimal("0.00"),
            ),
        )
        .order_by(
            "-total_purchase_value",
            "supplier__name",
        )
    )

    payment_data = (
        SupplierPayment.objects
        .values("supplier_id")
        .annotate(
            paid_amount=Coalesce(
                Sum("amount"),
                Decimal("0.00"),
            ),
        )
    )

    payments_by_supplier = {
        row["supplier_id"]: row["paid_amount"]
        for row in payment_data
    }

    results = []

    for supplier in purchase_data:
        supplier_id = supplier["supplier_id"]

        total_purchase_value = (
            supplier["total_purchase_value"]
            or Decimal("0.00")
        ).quantize(
            TWO_PLACES,
            rounding=ROUND_HALF_UP,
        )

        paid_amount = (
            payments_by_supplier.get(
                supplier_id,
                Decimal("0.00"),
            )
            or Decimal("0.00")
        ).quantize(
            TWO_PLACES,
            rounding=ROUND_HALF_UP,
        )

        outstanding_balance = (
            total_purchase_value - paid_amount
        ).quantize(
            TWO_PLACES,
            rounding=ROUND_HALF_UP,
        )

        results.append(
            {
                "supplier_id": supplier_id,
                "supplier__name": supplier["supplier__name"],
                "purchase_count": supplier["purchase_count"],
                "total_purchase_value": total_purchase_value,
                "paid_amount": paid_amount,
                "outstanding_balance": outstanding_balance,
            }
        )

    return results[:limit]

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



def get_historical_price_analysis(
    product_id=None,
    start_date=None,
    end_date=None,
    limit=10,
):
    """
    Return product-level historical price analysis.

    Purchase prices are taken from PurchaseItem.unit_cost on
    completed purchases.

    Selling prices are taken from SaleItem.unit_price on
    completed sales.

    Current Product price fields are not used because they represent
    current master-data values rather than historical transaction
    snapshots.

    Optional date filters are applied to the completion date of the
    corresponding transaction.

    If product_id is provided, only that product is analyzed.

    Products are ranked by product name.

    Products with no completed purchase or sale history are excluded.
    """

    store_timezone = django_timezone.get_default_timezone()

    start_dt, end_dt = _date_range_bounds(
        start_date,
        end_date,
        store_timezone,
    )

    purchase_items = PurchaseItem.objects.filter(
        purchase__status=Purchase.Status.COMPLETED,
    )

    sale_items = SaleItem.objects.filter(
        sale__status=Sale.Status.COMPLETED,
    )

    if product_id is not None:
        purchase_items = purchase_items.filter(
            product_id=product_id,
        )

        sale_items = sale_items.filter(
            product_id=product_id,
        )

    if start_dt is not None:
        purchase_items = purchase_items.filter(
            purchase__completed_at__gte=start_dt,
        )

        sale_items = sale_items.filter(
            sale__completed_at__gte=start_dt,
        )

    if end_dt is not None:
        purchase_items = purchase_items.filter(
            purchase__completed_at__lt=end_dt,
        )

        sale_items = sale_items.filter(
            sale__completed_at__lt=end_dt,
        )

    purchase_stats = (
        purchase_items
        .values("product_id")
        .annotate(
            minimum_purchase_cost=Min("unit_cost"),
            maximum_purchase_cost=Max("unit_cost"),
            average_purchase_cost=Avg("unit_cost"),
        )
    )

    sale_stats = (
        sale_items
        .values("product_id")
        .annotate(
            minimum_sell_price=Min("unit_price"),
            maximum_sell_price=Max("unit_price"),
            average_sell_price=Avg("unit_price"),
        )
    )

    purchase_by_product = {
        row["product_id"]: row
        for row in purchase_stats
    }

    sale_by_product = {
        row["product_id"]: row
        for row in sale_stats
    }

    product_ids = sorted(
        set(purchase_by_product)
        | set(sale_by_product)
    )

    products = (
        Product.objects
        .filter(id__in=product_ids)
        .order_by("name")
    )

    latest_purchase_by_product = {}

    latest_purchases = (
        PurchaseItem.objects
        .filter(
            purchase__status=Purchase.Status.COMPLETED,
            product_id__in=product_ids,
        )
        .select_related("purchase")
        .order_by(
            "product_id",
            "-purchase__completed_at",
            "-id",
        )
    )

    for item in latest_purchases:
        if item.product_id not in latest_purchase_by_product:
            latest_purchase_by_product[item.product_id] = item

    latest_sale_by_product = {}

    latest_sales = (
        SaleItem.objects
        .filter(
            sale__status=Sale.Status.COMPLETED,
            product_id__in=product_ids,
        )
        .select_related("sale")
        .order_by(
            "product_id",
            "-sale__completed_at",
            "-id",
        )
    )

    for item in latest_sales:
        if item.product_id not in latest_sale_by_product:
            latest_sale_by_product[item.product_id] = item

    results = []

    for product in products:
        purchase = purchase_by_product.get(product.id)
        sale = sale_by_product.get(product.id)

        latest_purchase = latest_purchase_by_product.get(
            product.id,
        )

        latest_sale = latest_sale_by_product.get(
            product.id,
        )

        results.append(
            {
                "product_id": product.id,
                "product__name": product.name,

                "minimum_purchase_cost": (
                    purchase["minimum_purchase_cost"]
                    if purchase is not None
                    else Decimal("0.00")
                ).quantize(
                    TWO_PLACES,
                    rounding=ROUND_HALF_UP,
                ),

                "maximum_purchase_cost": (
                    purchase["maximum_purchase_cost"]
                    if purchase is not None
                    else Decimal("0.00")
                ).quantize(
                    TWO_PLACES,
                    rounding=ROUND_HALF_UP,
                ),

                "average_purchase_cost": (
                    purchase["average_purchase_cost"]
                    if purchase is not None
                    else Decimal("0.00")
                ).quantize(
                    TWO_PLACES,
                    rounding=ROUND_HALF_UP,
                ),

                "minimum_sell_price": (
                    sale["minimum_sell_price"]
                    if sale is not None
                    else Decimal("0.00")
                ).quantize(
                    TWO_PLACES,
                    rounding=ROUND_HALF_UP,
                ),

                "maximum_sell_price": (
                    sale["maximum_sell_price"]
                    if sale is not None
                    else Decimal("0.00")
                ).quantize(
                    TWO_PLACES,
                    rounding=ROUND_HALF_UP,
                ),

                "average_sell_price": (
                    sale["average_sell_price"]
                    if sale is not None
                    else Decimal("0.00")
                ).quantize(
                    TWO_PLACES,
                    rounding=ROUND_HALF_UP,
                ),

                "latest_purchase_cost": (
                    latest_purchase.unit_cost
                    if latest_purchase is not None
                    else Decimal("0.00")
                ),

                "latest_sell_price": (
                    latest_sale.unit_price
                    if latest_sale is not None
                    else Decimal("0.00")
                ),
            }
        )

    return results[:limit]