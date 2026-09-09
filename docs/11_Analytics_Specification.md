# Analytics Specification

## 1. Document Purpose

This document defines the analytical capabilities of the Store Management System.

The Analytics layer provides decision-support metrics derived from completed business transactions and current operational data.

Analytics are intentionally separated from the Reports layer:

* **Reports** answer: "What happened?"
* **Analytics** answer: "What should I pay attention to, and what patterns can I identify?"

The Analytics layer is designed to support:

* Sales performance analysis
* Revenue and profitability analysis
* Product performance analysis
* Category profitability analysis
* Inventory performance analysis
* Supplier purchasing analysis
* Historical price analysis
* Sales trend analysis

---

# 2. Analytics Design Principles

## 2.1 Completed Transactions Only

Analytics based on transactional activity include only transactions with:

```text
status = COMPLETED
```

Draft and cancelled transactions are excluded from normal analytical calculations.

Historical cancelled transactions remain available in the system for audit purposes but do not contribute to normal Analytics metrics.

---

## 2.2 Historical Transaction Snapshots

Analytics must use historical values stored on transaction items rather than current Product master-data values.

For sales:

```text
SaleItem.unit_price
SaleItem.unit_cost
```

For purchases:

```text
PurchaseItem.unit_cost
```

This prevents later changes to product prices or costs from rewriting historical analytical results.

---

## 2.3 Costing Methodology

V1 uses a **cost snapshot methodology**.

When a sale is completed:

```text
SaleItem.unit_cost
    =
Product.current_purchase_cost
```

The captured `unit_cost` becomes the historical cost snapshot for that sale item.

COGS is calculated as:

```text
COGS = quantity × historical unit_cost
```

No FIFO or weighted-average inventory costing is implemented in V1.

---

## 2.4 Monetary Precision

Monetary analytical values are represented using Python `Decimal`.

Final monetary values are rounded to two decimal places using:

```text
ROUND_HALF_UP
```

Intermediate COGS calculations use sufficient decimal precision before final monetary rounding.

---

## 2.5 Timezone Handling

The Analytics layer uses the configured store timezone:

```text
settings.TIME_ZONE
```

The timezone is obtained through Django's default timezone configuration.

Date filtering uses a half-open interval:

```text
[start_date 00:00:00,
 end_date + 1 day 00:00:00)
```

Therefore:

```text
start_date → inclusive
end_date   → inclusive
```

Internally the upper boundary is implemented using:

```text
completed_at < end_date + 1 day
```

This avoids precision-related boundary problems.

---

# 3. Date Filtering

Where supported, `start_date` and `end_date` filter transactions according to their completion timestamp.

For sales:

```text
Sale.completed_at
```

For purchases:

```text
Purchase.completed_at
```

The date boundaries are interpreted in the store's configured timezone.

Both date filtering and period aggregation use the same store timezone.

This ensures that a transaction near midnight is consistently assigned to the same business date throughout the Analytics layer.

---

# 4. Profitability Summary

## Function

```python
get_profitability_summary(
    start_date=None,
    end_date=None,
)
```

## Purpose

Provides an overall profitability summary for completed sales.

## Metrics

### Revenue

Revenue is based on:

```text
Sale.total_amount
```

This represents the final sale value after sale-level discounts.

### COGS

```text
COGS = Σ(quantity × SaleItem.unit_cost)
```

### Gross Profit

```text
Gross Profit = Revenue - COGS
```

### Gross Margin

```text
Gross Margin =
    Gross Profit / Revenue × 100
```

When revenue is zero:

```text
gross_margin = None
```

because gross margin is undefined when there is no revenue.

## Date Filtering

Optional date filters are applied to:

```text
Sale.completed_at
```

Only completed sales are included.

---

# 5. Top-Selling Products

## Function

```python
get_top_selling_products(
    start_date=None,
    end_date=None,
    limit=10,
)
```

## Purpose

Identifies products with the highest sales volume.

## Ranking

Products are ranked by:

```text
quantity_sold DESC
```

Product name is used as a deterministic secondary ordering criterion.

## Metrics

```text
product_id
product__name
quantity_sold
sales_count
gross_sales_value
```

Where:

```text
quantity_sold =
    Σ SaleItem.quantity
```

```text
sales_count =
    COUNT(DISTINCT Sale)
```

```text
gross_sales_value =
    Σ SaleItem.line_total
```

`gross_sales_value` represents gross line-item sales before sale-level discounts.

## Filtering

Only completed sales are included.

Products with no completed sales are not returned.

---

# 6. Slow-Moving Products

## Function

```python
get_slow_moving_products(
    start_date=None,
    end_date=None,
    limit=10,
)
```

## Purpose

Identifies products with the lowest sales activity.

## Ranking

Products are ranked by:

```text
quantity_sold ASC
```

Product name is used as a deterministic secondary ordering criterion.

## Metrics

```text
product_id
product__name
quantity_sold
sales_count
gross_sales_value
```

## Filtering

Only completed sales are included.

Products with no sales are excluded.

This function therefore identifies products that have sold but have comparatively low sales activity.

Products that have never sold are handled separately through Inventory Performance.

---

# 7. Product Profitability

## Function

```python
get_product_profitability(
    start_date=None,
    end_date=None,
    limit=10,
)
```

## Purpose

Measures profitability at the individual product level.

## Metrics

```text
product_id
product__name
quantity_sold
gross_sales_value
cogs
gross_profit
gross_margin
```

### Gross Sales Value

```text
gross_sales_value =
    Σ SaleItem.line_total
```

This is the gross value before sale-level discounts.

### COGS

```text
cogs =
    Σ(quantity × SaleItem.unit_cost)
```

### Gross Profit

```text
gross_profit =
    gross_sales_value - cogs
```

### Gross Margin

```text
gross_margin =
    gross_profit / gross_sales_value × 100
```

If gross sales value is zero:

```text
gross_margin = None
```

## Ranking

Products are ranked by:

```text
gross_profit DESC
```

The `limit` is applied **after ranking**.

This ensures that the returned products are actually the most profitable products rather than simply the products with the highest sales value.

---

# 8. Category Profitability

## Function

```python
get_category_profitability(
    start_date=None,
    end_date=None,
    limit=10,
)
```

## Purpose

Measures profitability at the product-category level.

## Metrics

```text
product__category_id
product__category__name
quantity_sold
gross_sales_value
cogs
gross_profit
gross_margin
```

Metrics are aggregated across all products belonging to the category.

## Ranking

Categories are ranked by:

```text
gross_profit DESC
```

Category name is used as a deterministic secondary ordering criterion.

The `limit` is applied after ranking.

## Filtering

Only completed sale items are included.

Categories with no completed sales are excluded.

---

# 9. Inventory Performance

## Function

```python
get_inventory_performance(
    start_date=None,
    end_date=None,
    limit=10,
)
```

## Purpose

Combines current inventory information with sales activity.

This function is intended to identify products that require inventory attention.

## Metrics

```text
product_id
product__name
current_stock
minimum_stock
quantity_sold
sales_count
gross_sales_value
stock_status
```

### Current Stock

Taken from:

```text
Product.current_stock
```

This represents the current operational inventory quantity.

### Minimum Stock

Taken from:

```text
Product.minimum_stock
```

### Quantity Sold

Calculated from completed sales during the selected period:

```text
Σ SaleItem.quantity
```

### Sales Count

Number of distinct completed sales containing the product.

### Gross Sales Value

```text
Σ SaleItem.line_total
```

This represents gross line-item value before sale-level discounts.

---

## 9.1 Stock Status

Stock status is calculated as follows.

### Out of Stock

```text
current_stock <= 0
```

Result:

```text
OUT_OF_STOCK
```

### Low Stock

```text
current_stock < minimum_stock
```

Result:

```text
LOW_STOCK
```

### Normal

```text
current_stock >= minimum_stock
```

Result:

```text
NORMAL
```

Out-of-stock status takes precedence over low-stock status.

---

## 9.2 Product Inclusion

Inventory Performance includes:

* Active products
* Inactive products
* Products with sales
* Products without sales

This is intentional because inventory analysis must also identify products that currently exist but have no sales activity.

---

## 9.3 Inventory Turnover Limitation

V1 does **not** calculate true inventory turnover.

A true turnover metric requires historical inventory levels or an inventory movement ledger that can support average inventory calculations.

V1 maintains operational stock using:

```text
Product.current_stock
```

Therefore Inventory Performance focuses on:

* Current stock
* Minimum stock
* Sales activity
* Sales volume
* Stock status

rather than claiming to calculate historical inventory turnover.

---

# 10. Supplier Analysis

## Function

```python
get_supplier_analysis(
    start_date=None,
    end_date=None,
    limit=10,
)
```

## Purpose

Analyzes supplier purchasing activity and current supplier financial position.

## Metrics

```text
supplier_id
supplier__name
purchase_count
total_purchase_value
paid_amount
outstanding_balance
```

---

## 10.1 Period Purchasing Metrics

The following metrics respect the selected date range:

```text
purchase_count
total_purchase_value
```

Only completed purchases are included.

### Purchase Count

```text
purchase_count =
    COUNT(completed purchases)
```

### Total Purchase Value

```text
total_purchase_value =
    Σ Purchase.total_amount
```

---

## 10.2 Current Supplier Financial Position

The following metrics represent the supplier's current financial position and are therefore **not date-filtered**:

```text
paid_amount
outstanding_balance
```

### Paid Amount

```text
paid_amount =
    Σ SupplierPayment.amount
```

### Outstanding Balance

```text
outstanding_balance =
    all completed purchase value
    - all supplier payments
```

This distinction is important.

A selected date range can therefore answer:

> How much did we purchase from this supplier during this period?

while the outstanding balance answers:

> How much do we currently owe this supplier?

The system must not calculate:

```text
period purchases - all-time payments
```

because that mixes two different time scopes.

---

## 10.3 Supplier Filtering

Draft and cancelled purchases are excluded.

Suppliers with no completed purchases in the selected period are excluded from the returned analytical ranking.

Suppliers are ranked by:

```text
total_purchase_value DESC
```

Supplier name is used as a deterministic secondary ordering criterion.

---

# 11. Historical Price Analysis

## Function

```python
get_historical_price_analysis(
    product_id=None,
    start_date=None,
    end_date=None,
    limit=10,
)
```

## Purpose

Analyzes historical purchase costs and selling prices using transaction snapshots.

Current Product pricing fields are deliberately not used for historical analysis.

---

# 11.1 Purchase Price Metrics

Purchase prices are taken from:

```text
PurchaseItem.unit_cost
```

for completed purchases.

Metrics:

```text
minimum_purchase_cost
maximum_purchase_cost
average_purchase_cost
latest_purchase_cost
```

---

# 11.2 Selling Price Metrics

Selling prices are taken from:

```text
SaleItem.unit_price
```

for completed sales.

Metrics:

```text
minimum_sell_price
maximum_sell_price
average_sell_price
latest_sell_price
```

---

# 11.3 Latest Price Definition

When a date range is provided, the latest purchase and selling prices are determined **within that selected date range**.

The latest record is determined using:

```text
transaction completion timestamp DESC
```

with:

```text
item ID DESC
```

as a deterministic tie-breaker.

Therefore:

```text
latest_purchase_cost
```

means the latest completed purchase cost for the product within the selected period.

Likewise:

```text
latest_sell_price
```

means the latest completed selling price for the product within the selected period.

---

# 11.4 Product Filtering

If:

```python
product_id
```

is provided, only that product is analyzed.

If no product is provided, multiple products may be returned.

Products are ordered by product name.

Products with no completed purchase or sale history are excluded.

---

# 11.5 Historical Price Integrity

Historical price analysis must never use:

```text
Product.current_purchase_cost
Product.current_sell_price
```

for historical transaction statistics.

These fields represent current master-data values.

Historical transaction records contain the appropriate snapshots needed for analytical reconstruction.

---

# 12. Sales Trend Analysis

## Function

```python
get_sales_trend(
    start_date=None,
    end_date=None,
    interval="day",
)
```

## Purpose

Analyzes sales activity over time.

Supported intervals:

```text
day
week
month
```

Any other interval value is invalid.

---

# 12.1 Daily Trend

For:

```python
interval="day"
```

sales are grouped by store-local calendar day.

---

# 12.2 Weekly Trend

For:

```python
interval="week"
```

sales are grouped by week.

Weeks start on:

```text
Monday
```

---

# 12.3 Monthly Trend

For:

```python
interval="month"
```

sales are grouped by the first day of the month.

---

# 12.4 Sales Trend Metrics

Each period returns:

```text
date
transaction_count
units_sold
gross_sales_value
revenue
```

### Transaction Count

```text
COUNT(completed sales)
```

### Units Sold

```text
Σ SaleItem.quantity
```

### Gross Sales Value

```text
Σ SaleItem.line_total
```

### Revenue

```text
Σ Sale.total_amount
```

Revenue reflects sale-level discounts.

---

# 12.5 Separate Aggregation

Sale-level and item-level metrics are aggregated separately.

This prevents a sale's total revenue from being duplicated when a sale contains multiple sale items.

For example:

```text
Sale A
    total_amount = 100

    Item 1
    Item 2
    Item 3
```

The revenue must remain:

```text
100
```

not:

```text
300
```

Therefore:

```text
Sale
    ↓
sale-level aggregation
```

and:

```text
SaleItem
    ↓
item-level aggregation
```

are calculated independently and combined by period.

---

# 13. Discounts and Analytical Semantics

V1 supports sale-level discounts.

There is no item-level discount allocation mechanism.

Therefore two different revenue concepts exist in Analytics.

## Final Revenue

Used by overall profitability:

```text
Sale.total_amount
```

This reflects the actual final sale amount after discount.

## Gross Sales Value

Used by product, category, inventory, and sales-trend item metrics:

```text
Σ SaleItem.line_total
```

This represents the gross value before sale-level discount.

---

## 13.1 V1 Limitation

Product-level and category-level profitability do not allocate sale-level discounts among individual products.

Consequently:

```text
Product Gross Profit =
    Gross Sales Value - COGS
```

rather than:

```text
Discount-adjusted Product Revenue - COGS
```

This is an intentional V1 limitation.

A future version may introduce a defined discount-allocation methodology if detailed net product profitability is required.

---

# 14. Draft and Cancelled Transactions

Analytics must exclude:

```text
DRAFT
CANCELLED
```

transactions from normal analytical metrics.

Only:

```text
COMPLETED
```

transactions contribute to:

* Revenue
* COGS
* Gross Profit
* Sales Volume
* Product Performance
* Category Performance
* Supplier Purchase Activity
* Historical Price Statistics
* Sales Trends

Cancellation does not erase the historical transaction.

Instead, cancelled transactions remain available for audit purposes while being excluded from normal analytical totals.

---

# 15. Historical Data Preservation

Analytics depend on transaction snapshots remaining unchanged.

Changing:

```text
Product.current_purchase_cost
Product.current_sell_price
Product.name
Product.category
```

must not rewrite the historical monetary values stored on completed transaction items.

Historical sales continue to use:

```text
SaleItem.unit_price
SaleItem.unit_cost
```

Historical purchases continue to use:

```text
PurchaseItem.unit_cost
```

---

# 16. Analytics API Summary

| Function                          | Primary Purpose                       | Ranking / Grouping  |
| --------------------------------- | ------------------------------------- | ------------------- |
| `get_profitability_summary()`     | Overall profitability                 | Summary             |
| `get_top_selling_products()`      | Best-selling products                 | Quantity sold DESC  |
| `get_slow_moving_products()`      | Low-sales products                    | Quantity sold ASC   |
| `get_product_profitability()`     | Product profitability                 | Gross profit DESC   |
| `get_category_profitability()`    | Category profitability                | Gross profit DESC   |
| `get_inventory_performance()`     | Stock + sales performance             | Quantity sold DESC  |
| `get_supplier_analysis()`         | Supplier purchasing + current balance | Purchase value DESC |
| `get_historical_price_analysis()` | Historical costs/prices               | Product name        |
| `get_sales_trend()`               | Sales trends over time                | Day / Week / Month  |

---

# 17. Analytics vs Reports

The system deliberately maintains separate Reports and Analytics layers.

## Reports

Reports provide operational information such as:

* Sales Summary
* Expense Summary
* Inventory Report
* Low Stock Report
* Customer Debt Report
* Supplier Balance Report

Reports are primarily concerned with:

```text
What happened?
```

## Analytics

Analytics provide decision-support information such as:

* Profitability
* Top products
* Slow-moving products
* Product profitability
* Category profitability
* Inventory performance
* Supplier purchasing performance
* Historical pricing
* Sales trends

Analytics are primarily concerned with:

```text
What patterns exist?
What is performing well?
What requires attention?
```

The two layers may use some of the same underlying models and calculations, but they serve different business purposes and should remain logically separated.

---

# 18. V1 Limitations

The following capabilities are intentionally outside the V1 Analytics scope.

## 18.1 No FIFO Costing

V1 does not implement FIFO inventory costing.

## 18.2 No Weighted Average Costing

V1 does not implement weighted-average inventory costing.

## 18.3 No Historical Inventory Ledger

V1 does not maintain a dedicated inventory movement ledger.

## 18.4 No True Inventory Turnover

True inventory turnover is not calculated because historical average inventory is unavailable.

## 18.5 No Product-Level Discount Allocation

Sale-level discounts are not allocated to individual products or categories.

## 18.6 No Advanced Forecasting

V1 does not provide:

* Demand forecasting
* Time-series forecasting
* Reorder prediction
* Machine-learning-based sales prediction

These may be considered in future versions.

## 18.7 No Automated Cost Updates

Completing a purchase does not automatically change:

```text
Product.current_purchase_cost
```

The current product purchase cost is maintained separately from historical purchase transactions.

---

# 19. Performance Considerations

The Analytics layer should prefer database aggregation over loading complete transaction datasets into Python.

Examples include:

```text
Sum
Count
Avg
Min
Max
ExpressionWrapper
```

Grouping and ranking should be performed by the database whenever practical.

The `limit` must be applied after the relevant analytical ranking.

For example:

```text
ORDER BY gross_profit DESC
LIMIT 10
```

rather than:

```text
LIMIT 10
ORDER BY gross_profit DESC
```

The current V1 implementation is designed for the expected scale of a single-store application and avoids unnecessary analytical infrastructure.

Future optimization may include:

* Additional database indexes
* Query optimization
* Materialized analytical views
* Cached dashboard KPIs
* Background aggregation

These should only be introduced when actual performance requirements justify them.

---

# 20. Testing Requirements

Every Analytics function must be tested against the relevant business rules.

Tests should cover, where applicable:

* Empty datasets
* Normal calculations
* Multiple records
* Multiple products
* Multiple categories
* Draft transactions
* Cancelled transactions
* Completed transactions
* Date ranges
* Boundary dates
* Store timezone behavior
* Limits
* Ranking before limiting
* Zero revenue
* Zero sales activity
* Products with no sales
* Historical price selection
* Supplier current balance calculation

Particular attention should be given to ensuring that:

```text
date filtering
```

and:

```text
timezone conversion
```

produce deterministic results.

---

# 21. Current Analytics Service Contract

The Analytics service layer currently provides:

```text
get_profitability_summary()
get_top_selling_products()
get_slow_moving_products()
get_product_profitability()
get_category_profitability()
get_inventory_performance()
get_supplier_analysis()
get_historical_price_analysis()
get_sales_trend()
```

These functions form the V1 analytical service API.

The UI layer should consume these services rather than duplicating business calculations inside views or templates.

---

# 22. Future Dashboard Integration

The Analytics service layer is designed to support a future dashboard.

Potential dashboard components include:

### KPI Cards

* Revenue
* COGS
* Gross Profit
* Gross Margin

### Sales Visualization

* Daily sales
* Weekly sales
* Monthly sales
* Revenue trend

### Product Analysis

* Top-selling products
* Slow-moving products
* Most profitable products
* Product margins

### Category Analysis

* Category revenue
* Category gross profit
* Category margin

### Inventory Alerts

* Out-of-stock products
* Low-stock products
* High-volume products with low current stock

### Supplier Analysis

* Highest purchasing suppliers
* Purchase value
* Current outstanding balances

### Price Analysis

* Historical purchase cost
* Historical selling price
* Latest transaction prices
* Price ranges

The dashboard should consume the Analytics service layer rather than reimplementing calculations.

---

# 23. V1 Architectural Position

The Analytics layer is a **service layer**, not a separate analytics database or data warehouse.

The V1 architecture is:

```text
Django Models
      ↓
Business Services
      ↓
Analytics Services
      ↓
Views / API
      ↓
Dashboard / Reports UI
```

The Analytics layer should remain independent of presentation concerns.

It should return structured Python data suitable for:

* Django templates
* Django views
* Future REST API endpoints
* Dashboard components
* Export functionality

---

# 24. Acceptance Criteria

The Analytics implementation is considered complete for V1 when:

* [x] Completed transactions are included.
* [x] Draft transactions are excluded.
* [x] Cancelled transactions are excluded.
* [x] Historical cost snapshots are used for COGS.
* [x] Profitability summary calculates revenue, COGS, gross profit, and margin.
* [x] Top-selling products are supported.
* [x] Slow-moving products are supported.
* [x] Product profitability is supported.
* [x] Category profitability is supported.
* [x] Inventory performance is supported.
* [x] Supplier purchasing analysis is supported.
* [x] Current supplier outstanding balance uses all completed purchases and all payments.
* [x] Historical purchase-price analysis is supported.
* [x] Historical selling-price analysis is supported.
* [x] Latest historical prices respect the selected date range.
* [x] Sales trends support daily, weekly, and monthly intervals.
* [x] Date filtering uses the store timezone.
* [x] Date ranges use inclusive start/end dates.
* [x] Database aggregation is used for analytical calculations where practical.
* [x] Ranking occurs before applying result limits.
* [x] Sale-level and item-level metrics are aggregated separately where required.
* [x] V1 limitations are explicitly documented.

---

# 25. Conclusion

The V1 Analytics layer provides a focused analytical foundation for the Store Management System.

It converts completed operational transactions and current inventory information into decision-support metrics without introducing unnecessary architectural complexity.

The design prioritizes:

* Correct business semantics
* Historical data integrity
* Deterministic timezone handling
* Accurate monetary calculations
* Database-level aggregation
* Clear separation from operational Reports
* Testability
* Future dashboard integration

The Analytics layer is therefore ready to serve as the backend foundation for the system's future management dashboard.
