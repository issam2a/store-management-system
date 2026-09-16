from datetime import timedelta

from django.db.models import F, Sum
from django.shortcuts import render
from django.utils import timezone

from apps.analytics.services import (
    get_executive_kpis,
    get_sales_trend,
    get_top_selling_products,
)
from apps.products.models import Product
from apps.sales.models import Sale, SaleItem


def home(request):
    today = timezone.localdate()

    # ---------------------------------------------------------
    # Executive KPIs
    # ---------------------------------------------------------

    kpis = get_executive_kpis(
        start_date=today,
        end_date=today,
    )
    print("DASHBOARD KPIS:", kpis)

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
        Sale.objects
        .filter(
            status=Sale.Status.COMPLETED,
        )
        .select_related("customer")
        .order_by("-completed_at")[:5]
    )

    # ---------------------------------------------------------
    # Top products
    #
    # Ranked by quantity sold.
    # ---------------------------------------------------------

    top_products = get_top_selling_products(
        start_date=today,
        end_date=today,
    )

    # ---------------------------------------------------------
# Revenue trend — last 7 days
# ---------------------------------------------------------

    start_date = today - timedelta(days=6)

    sales_trend = get_sales_trend(
        start_date=start_date,
        end_date=today,
    )

    trend_by_date = {
        item["date"]: item
        for item in sales_trend
    }

    chart_data = []

    for offset in range(7):
        date = start_date + timedelta(days=offset)

        item = trend_by_date.get(date)

        chart_data.append(
            {
                "date": date.isoformat(),
                "label": date.strftime("%a"),
                "revenue": float(
                    item["revenue"]
                    if item
                    else 0
                ),
                "transactions": int(
                    item["transaction_count"]
                    if item
                    else 0
                ),
                "units_sold": float(
                    item["units_sold"]
                    if item
                    else 0
                ),
            }
        )

    # ---------------------------------------------------------
    # Dashboard context
    # ---------------------------------------------------------

    context = {
        "today": today,

        # Executive KPIs
        "revenue": kpis["revenue"],
        "cogs": kpis["cogs"],
        "gross_profit": kpis["gross_profit"],
        "gross_margin": kpis["gross_margin"],
        "sales_count": kpis["transaction_count"],
        "units_sold": kpis["units_sold"],
        "average_order_value": kpis["average_order_value"],

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