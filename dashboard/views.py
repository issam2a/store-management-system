from datetime import timedelta
from decimal import Decimal

from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.db.models.functions import TruncDay
from django.shortcuts import render
from django.utils import timezone

from apps.products.models import Product
from apps.sales.models import Sale, SaleItem


def home(request):
    today = timezone.localdate()

    # ---------------------------------------------------------
    # Completed sales only
    # ---------------------------------------------------------

    completed_sales = Sale.objects.filter(
        status=Sale.Status.COMPLETED,
    )

    # ---------------------------------------------------------
    # Today's KPIs
    # ---------------------------------------------------------

    today_sales = completed_sales.filter(
        completed_at__date=today,
    )

    revenue = (
        today_sales.aggregate(
            total=Sum("total_amount")
        )["total"]
        or Decimal("0.00")
    )

    sales_count = today_sales.count()

    # ---------------------------------------------------------
    # Today's COGS
    # ---------------------------------------------------------

    today_sale_items = SaleItem.objects.filter(
        sale__in=today_sales,
    )

    cogs_expression = ExpressionWrapper(
        F("quantity") * F("unit_cost"),
        output_field=DecimalField(
            max_digits=18,
            decimal_places=2,
        ),
    )

    cogs = (
        today_sale_items.aggregate(
            total=Sum(cogs_expression)
        )["total"]
        or Decimal("0.00")
    )

    gross_profit = revenue - cogs

    # ---------------------------------------------------------
    # Low stock
    #
    # Business rule:
    # current_stock < minimum_stock
    # ---------------------------------------------------------

    low_stock_products = (
        Product.objects
        .filter(
            is_active=True,
            current_stock__lt=F("minimum_stock"),
        )
        .select_related("unit", "category")
        .order_by(
            "current_stock",
            "name",
        )
    )

    low_stock_count = low_stock_products.count()

    low_stock_products_display = low_stock_products[:5]

    # ---------------------------------------------------------
    # Recent completed sales
    # ---------------------------------------------------------

    recent_sales = (
        completed_sales
        .select_related("customer")
        .order_by("-completed_at")[:5]
    )

    # ---------------------------------------------------------
    # Top products
    #
    # Ranked by quantity sold.
    # Cancelled sales are excluded because we filter by
    # COMPLETED status.
    # ---------------------------------------------------------

    top_products = (
        SaleItem.objects
        .filter(
            sale__status=Sale.Status.COMPLETED,
        )
        .values(
            "product_id",
            "product__name",
            "product__unit__symbol",
        )
        .annotate(
            quantity_sold=Sum("quantity"),
            revenue=Sum("line_total"),
        )
        .order_by(
            "-quantity_sold",
            "product__name",
        )[:5]
    )

    # ---------------------------------------------------------
    # Revenue trend — last 7 days
    # ---------------------------------------------------------

    start_date = today - timedelta(days=6)

    revenue_trend = (
        completed_sales
        .filter(
            completed_at__date__gte=start_date,
            completed_at__date__lte=today,
        )
        .annotate(
            day=TruncDay("completed_at"),
        )
        .values("day")
        .annotate(
            revenue=Sum("total_amount"),
        )
        .order_by("day")
    )

    revenue_by_day = {
        item["day"].date(): item["revenue"]
        for item in revenue_trend
    }

    chart_data = []

    for offset in range(7):
        date = start_date + timedelta(days=offset)

        chart_data.append(
            {
                "date": date.isoformat(),
                "label": date.strftime("%a"),
                "revenue": float(
                    revenue_by_day.get(
                        date,
                        Decimal("0.00"),
                    )
                ),
            }
        )

    context = {
        "today": today,

        # KPIs
        "revenue": revenue,
        "sales_count": sales_count,
        "cogs": cogs,
        "gross_profit": gross_profit,

        # Inventory
        "low_stock_count": low_stock_count,
        "low_stock_products": low_stock_products_display,

        # Tables
        "recent_sales": recent_sales,
        "top_products": top_products,

        # Chart
        "chart_data": chart_data,
    }

    return render(
        request,
        "dashboard/home.html",
        context,
    )