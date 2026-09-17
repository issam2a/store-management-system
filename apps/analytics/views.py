from datetime import timedelta

from django.shortcuts import render
from django.utils import timezone

from .services import (
    get_executive_kpis,
    get_sales_trend,
)


def analytics_dashboard(request):
    today = timezone.localdate()
    start_date = today - timedelta(days=29)

    kpis = get_executive_kpis(
        start_date=start_date,
        end_date=today,
    )

    sales_trend = get_sales_trend(
        start_date=start_date,
        end_date=today,
        interval="day",
    )

    trend_by_date = {
        item["date"]: item
        for item in sales_trend
    }

    chart_data = []

    for offset in range(30):
        date = start_date + timedelta(days=offset)

        item = trend_by_date.get(date)

        chart_data.append(
            {
                "date": date.isoformat(),
                "label": date.strftime("%b %d"),
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

    context = {
        "today": today,
        "start_date": start_date,
        "kpis": kpis,
        "chart_data": chart_data,
    }

    return render(
        request,
        "analytics/dashboard.html",
        context,
    )