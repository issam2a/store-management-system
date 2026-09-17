from datetime import timedelta

from django.shortcuts import render
from django.utils import timezone

from .services import (
    get_executive_kpis,
    get_sales_trend,
    get_top_selling_products,
    get_slow_moving_products,
    get_product_profitability,
    get_category_profitability,
    get_profitability_trend,
    get_sales_by_day_of_week,
    get_sales_by_hour,
)


def analytics_dashboard(request):
    today = timezone.localdate()

    selected_range = request.GET.get("range", "30")

    # Default range: 30 days
    start_date = today - timedelta(days=29)
    end_date = today

    if selected_range == "today":
        start_date = today

    elif selected_range == "7":
        start_date = today - timedelta(days=6)

    elif selected_range == "30":
        start_date = today - timedelta(days=29)

    elif selected_range == "custom":
        custom_start = request.GET.get("start_date")
        custom_end = request.GET.get("end_date")

        try:
            if custom_start and custom_end:
                start_date = timezone.datetime.strptime(
                    custom_start,
                    "%Y-%m-%d",
                ).date()

                end_date = timezone.datetime.strptime(
                    custom_end,
                    "%Y-%m-%d",
                ).date()

                if start_date > end_date:
                    start_date = today - timedelta(days=29)
                    end_date = today
                    selected_range = "30"

        except ValueError:
            start_date = today - timedelta(days=29)
            end_date = today
            selected_range = "30"

    # ---------------------------------------------------------
    # Executive KPIs
    # ---------------------------------------------------------

    kpis = get_executive_kpis(
        start_date=start_date,
        end_date=end_date,
    )

    # ---------------------------------------------------------
    # Sales Trend
    # ---------------------------------------------------------

    sales_trend = get_sales_trend(
        start_date=start_date,
        end_date=end_date,
        interval="day",
    )

    trend_by_date = {
        item["date"]: item
        for item in sales_trend
    }

    chart_data = []

    current_date = start_date

    while current_date <= end_date:
        item = trend_by_date.get(current_date)

        chart_data.append({
            "date": current_date.isoformat(),
            "label": current_date.strftime("%b %d"),
            "revenue": float(
                item["revenue"] if item else 0
            ),
            "transactions": int(
                item["transaction_count"] if item else 0
            ),
            "units_sold": float(
                item["units_sold"] if item else 0
            ),
        })

        current_date += timedelta(days=1)

    # ---------------------------------------------------------
    # Product Performance
    # ---------------------------------------------------------

    top_selling_products = get_top_selling_products(
        start_date=start_date,
        end_date=end_date,
        limit=5,
    )

    slow_moving_products = get_slow_moving_products(
        start_date=start_date,
        end_date=end_date,
        limit=5,
    )

    # ---------------------------------------------------------
    # Product Profitability
    # ---------------------------------------------------------

    product_profitability = get_product_profitability(
        start_date=start_date,
        end_date=end_date,
    )

    # ---------------------------------------------------------
    # Profitability Trend
    # ---------------------------------------------------------

    profitability_trend = get_profitability_trend(
        start_date=start_date,
        end_date=end_date,
    )

    profitability_chart_data = []

    for item in profitability_trend:
        profitability_chart_data.append({
            "date": item["date"].isoformat(),
            "label": item["date"].strftime("%b %d"),
            "revenue": float(item["revenue"]),
            "cogs": float(item["cogs"]),
            "gross_profit": float(item["gross_profit"]),
        })

    # ---------------------------------------------------------
    # Category Profitability
    # ---------------------------------------------------------

    category_profitability = get_category_profitability(
        start_date=start_date,
        end_date=end_date,
    )

    category_chart_data = []

    for category in category_profitability:
        category_chart_data.append({
            "name": category["category_name"],
            "revenue": float(
                category["gross_sales_value"]
            ),
            "gross_profit": float(
                category["gross_profit"]
            ),
            "cogs": float(
                category["cogs"]
            ),
        })


    # ------------------------------------------------------------
    # day of week
    #-------------------------------------------------------------

    sales_by_day_of_week = get_sales_by_day_of_week(
        start_date=start_date,
        end_date=end_date,
    )


    # ------------------------------------------------------------
    # sale by hour 
    #-------------------------------------------------------------
    sales_by_hour = get_sales_by_hour(
        start_date=start_date,
        end_date=end_date,
    )

    day_of_week_chart_data = [
        {
            "label": item["day_name"],
            "transactions": item["transaction_count"],
            "revenue": float(item["revenue"]),
            "average_order_value": float(item["average_order_value"]),
        }
        for item in sales_by_day_of_week
    ]

    hourly_sales_chart_data = [
        {
            "hour": item["hour"],
            "label": f"{item['hour']:02d}:00",
            "transactions": item["transaction_count"],
            "revenue": float(item["revenue"]),
            "average_order_value": float(item["average_order_value"]),
        }
        for item in sales_by_hour
    ]
    context = {
        "today": today,
        "start_date": start_date,
        "end_date": end_date,

        "selected_range": selected_range,

        "kpis": kpis,

        "chart_data": chart_data,

        "top_selling_products": top_selling_products,
        "slow_moving_products": slow_moving_products,

        "product_profitability": product_profitability,

        "profitability_chart_data": profitability_chart_data,
        "category_profitability": category_profitability,
        "category_chart_data": category_chart_data,

        "day_of_week_chart_data": day_of_week_chart_data,
        "hourly_sales_chart_data": hourly_sales_chart_data,
    }

    return render(
        request,
        "analytics/dashboard.html",
        context,
    )