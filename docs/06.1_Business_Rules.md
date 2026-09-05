# Store Management & Business Analytics System

# Business Rules

**Document ID:** BRL-001
**Version:** 1.0
**Status:** Draft
**Author:** Issam
**Date:** September 2026

**Related Documents:**

* `01_Project_Charter.md`
* `02_Business_Requirements.md`
* `03_Functional_Requirements.md`
* `04_Use_Cases.md`
* `05_System_Architecture.md`
* `06_Database_Design.md`

---

# 1. Purpose

This document defines the business rules governing the Store Management & Business Analytics System.

Business rules define the conditions, constraints, calculations, and behavioral principles that the system must enforce regardless of the user interface or implementation technology.

Business rules are identified using:

```text
BRL-XXX
```

Where:

* `BRL` = Business Rule
* `XXX` = unique rule number

Business requirements use `BR-XXX`, while functional requirements use `FR-XXX`.

---

# 2. Product and Reference Data Rules

## BRL-001 — Product Registration

A product shall have the required product information before it can be used in purchasing, sales, or inventory operations.

**Related:** BR-001, FR-005

---

## BRL-002 — Product Category

Each product shall belong to a product category.

Categories may be created, updated, viewed, and deactivated by authorized users.

**Related:** BR-002, FR-007

---

## BRL-003 — Unit of Measurement

Each inventory-controlled product shall have a defined unit of measurement.

Examples include kilogram, gram, piece, box, and package.

**Related:** BR-003, FR-008

---

## BRL-004 — Reference Data Deactivation

A category or unit that is referenced by existing products or historical transactions shall not be physically deleted.

It shall be deactivated when it should no longer be available for new operations.

**Related:** BR-002, BR-003, FR-007, FR-008

---

## BRL-005 — Product Identifier

Each product shall have a unique internal identifier.

SKU or barcode support may be provided where applicable.

The exact SKU/barcode behavior remains subject to final business confirmation.

**Related:** BR-007, FR-012

---

# 3. Product Pricing Rules

## BRL-006 — Current Default Selling Price

Each product may have a current/default selling price used as the default price when creating new sales.

**Related:** BR-004, FR-009

---

## BRL-007 — Current Default Purchase Cost

Each product may have a current/default purchase cost used as the default cost when creating new purchases.

**Related:** BR-004, FR-009

---

## BRL-008 — Actual Transaction Price

The actual unit selling price used in a sale shall be stored with the sale item.

The actual unit purchase cost used in a purchase shall be stored with the purchase item.

**Related:** BR-005, FR-010

---

## BRL-009 — Historical Price Immutability

Changing a product's current/default selling price or purchase cost shall not modify prices or costs stored in completed historical transactions.

**Related:** BR-005, FR-009, FR-010, FR-089

---

## BRL-010 — Purchase Cost Override

The actual purchase cost recorded for a purchase item may differ from the product's current/default purchase cost.

The actual transaction cost shall be preserved.

**Related:** BR-011, FR-024

---

## BRL-011 — Purchase Cost Does Not Automatically Change Product Default

Recording an actual purchase cost shall not automatically overwrite the product's current/default purchase cost.

Updating the product's default purchase cost is a separate product-management operation.

**Related:** BR-004, BR-011

---

# 4. Purchase Rules

## BRL-012 — Purchase Lifecycle

A purchase shall follow:

```text
Draft → Completed → Cancelled
```

A cancelled purchase cannot return to the Completed state.

**Related:** BR-008, BR-078, BR-089, BR-090

---

## BRL-013 — Draft Purchase

A draft purchase shall not affect inventory or official financial balances.

Draft purchases may be edited by authorized users.

**Related:** FR-023, FR-028

---

## BRL-014 — Multiple Purchase Items

A purchase may contain multiple purchase items.

Each item shall identify the product, quantity, unit, actual purchase cost, and line total.

**Related:** BR-009, BR-010, BR-011, FR-024

---

## BRL-015 — Purchase Total

The purchase total shall equal the sum of its purchase-item totals.

```text
Purchase Total =
Σ (Quantity × Actual Purchase Cost)
```

**Related:** FR-025

---

## BRL-016 — Purchase Completion

Only a completed purchase shall affect inventory and financial balances.

**Related:** FR-028

---

## BRL-017 — Purchase Inventory Effect

When a purchase is completed, the purchased quantity of each applicable product shall be added to inventory.

**Related:** BR-027, FR-029

---

## BRL-018 — Cash Purchase

A cash purchase shall be treated as paid at completion according to the recorded transaction/payment information.

It shall not create an outstanding supplier balance for the amount already paid.

**Related:** BR-012, FR-026

---

## BRL-019 — Credit Purchase

A credit purchase creates an amount payable to the supplier for the unpaid portion of the purchase.

**Related:** BR-013, BR-014, FR-027

---

## BRL-020 — Partial Purchase Payment

A purchase may be partially paid.

The unpaid portion becomes part of the supplier's outstanding balance.

```text
Supplier Outstanding =
Amount Due − Applicable Payments
```

**Related:** BR-013, BR-051, FR-027, FR-046

---

# 5. Sales Rules

## BRL-021 — Sale Lifecycle

A sale shall follow:

```text
Draft → Completed → Cancelled
```

A cancelled sale cannot return to the Completed state.

**Related:** BR-016, BR-089, BR-090

---

## BRL-022 — Draft Sale

A draft sale shall not affect inventory or official financial balances.

Draft sales may be edited by authorized users.

**Related:** FR-033, FR-039

---

## BRL-023 — Multiple Sale Items

A sale may contain multiple sale items.

Each item shall identify the product, quantity, unit, actual selling price, and line total.

**Related:** BR-017, BR-018, BR-019, FR-034

---

## BRL-024 — Sale Subtotal

The sale subtotal shall equal:

```text
Subtotal =
Σ (Quantity × Actual Selling Price)
```

**Related:** BR-016, FR-035

---

## BRL-025 — Sale Discount

An authorized user may apply an approved discount to a sale.

The original sale-item prices shall remain preserved.

The discount shall be recorded separately and shall affect the final amount due.

**Related:** BR-020, FR-036

---

## BRL-026 — Discount Rules Remain Configurable

The exact discount mechanism remains subject to business confirmation, including:

* percentage versus fixed amount;
* sale-level versus item-level discount;
* maximum permitted discount;
* required authorization;
* profitability restrictions.

These details shall not be assumed until finalized.

**Related:** BR-020, FR-036

---

## BRL-027 — Sale Completion

Only a completed sale shall affect inventory and official financial records.

**Related:** FR-039

---

## BRL-028 — Sufficient Inventory

A sale shall not be completed if the available inventory is insufficient for any sale item, unless a future business decision explicitly permits negative inventory.

The negative-inventory policy remains an open decision.

**Related:** BR-026, FR-040

---

## BRL-029 — Sale Inventory Effect

When a sale is completed, the quantity sold for each applicable product shall be deducted from inventory.

**Related:** BR-028, FR-040

---

## BRL-030 — Cash Sale

A cash sale shall be fully paid at the time of completion.

**Related:** BR-021, FR-037

---

## BRL-031 — Credit Sale

A credit sale may have an unpaid amount.

The unpaid amount becomes part of the customer's outstanding balance.

**Related:** BR-022, BR-024, FR-038

---

## BRL-032 — Customer Required for Credit Sale

A credit sale shall require an identified customer account.

A cash sale does not require a customer record.

**Related:** BR-022, FR-038

---

## BRL-033 — Customer Optional for Cash Sale

Walk-in cash customers shall not require customer records.

When no customer account is required, the sale may be recorded without a customer.

**Related:** BR-021, FR-033

---

# 6. Customer Rules

## BRL-034 — Customer Account

Customer records shall primarily support credit transactions, account tracking, purchase history, and payment history.

**Related:** BR-035–BR-039, FR-013–FR-017

---

## BRL-035 — Customer Outstanding Balance

A customer's outstanding balance shall be calculated from applicable completed credit sales and customer payments.

**Related:** BR-039, FR-017

---

## BRL-036 — Customer Payment

A customer payment shall reduce the customer's outstanding balance.

It shall not modify the original sale.

**Related:** BR-023, BR-038, FR-016, FR-044

---

## BRL-037 — Customer Payment Cannot Exceed Allowed Balance

A customer payment shall not exceed the customer's allowed outstanding balance unless a future business rule explicitly permits overpayment.

V1 does not support overpayments.

**Related:** BR-051, FR-048

---

# 7. Supplier Rules

## BRL-038 — Supplier Account

Supplier records shall support purchases, purchase history, payments, and outstanding balances.

**Related:** BR-040–BR-044, FR-018–FR-022

---

## BRL-039 — Supplier Outstanding Balance

A supplier's outstanding balance shall be calculated from applicable completed credit purchases and supplier payments.

**Related:** BR-044, FR-022

---

## BRL-040 — Supplier Payment

A supplier payment shall reduce the supplier's outstanding balance.

It shall not modify the original purchase.

**Related:** BR-043, BR-044, FR-021, FR-044

---

## BRL-041 — Supplier Payment Cannot Exceed Allowed Balance

A supplier payment shall not exceed the allowed outstanding supplier balance unless overpayment is explicitly supported by a future business decision.

V1 does not support supplier overpayments.

**Related:** BR-051, FR-048

---

# 8. Payment Rules

## BRL-042 — Payment Recording

Payments shall be recorded as separate business records.

**Related:** BR-049, BR-052, FR-044

---

## BRL-043 — Payment Method

Each payment shall record its payment method.

The exact supported payment methods shall remain configurable until finalized with the business.

**Related:** BR-050, FR-045

---

## BRL-044 — Partial Payments

The system shall support partial settlement of customer and supplier balances.

**Related:** BR-051, FR-046

---

## BRL-045 — Payment Validation

Payment amounts shall be positive and valid.

Zero and negative payments shall not be accepted.

**Related:** FR-048

---

## BRL-046 — Payment History Preservation

Payment records shall be preserved for audit and historical reporting.

Payments shall not be physically deleted in a manner that destroys financial history.

**Related:** BR-052, BR-082, FR-047

---

# 9. Inventory Rules

## BRL-047 — Current Stock

The product's current stock quantity shall represent the operational inventory quantity in V1.

**Related:** BR-026, FR-049

---

## BRL-048 — Purchase Inventory Increase

A completed purchase increases the applicable product inventory.

Draft purchases do not change inventory.

**Related:** BR-027, FR-029

---

## BRL-049 — Sale Inventory Decrease

A completed sale decreases the applicable product inventory.

Draft sales do not change inventory.

**Related:** BR-028, FR-040

---

## BRL-050 — Inventory Adjustment

Authorized users may adjust inventory when the physical quantity differs from the system quantity.

An adjustment shall require a reason.

**Related:** BR-031, FR-052

---

## BRL-051 — Inventory History

The system shall preserve sufficient information to review inventory changes caused by:

* completed purchases;
* completed sales;
* inventory adjustments;
* transaction cancellations.

V1 does not require a separate `InventoryMovement` table.

**Related:** BR-032, FR-050, FR-051, FR-054

---

## BRL-052 — Inventory Movement Traceability

Each inventory change shall be traceable to the business transaction or adjustment that caused it.

**Related:** BR-032, FR-051

---

## BRL-053 — Low Stock

A product shall be considered low stock when its available quantity is below its configured minimum stock level.

**Related:** BR-033, FR-053

---

## BRL-054 — Inventory Valuation

The system shall support inventory valuation using an approved inventory costing methodology.

The exact costing methodology remains to be finalized.

**Related:** BR-034, FR-055

---

## BRL-055 — Direct Stock Modification

Operational inventory shall not be changed directly without an authorized business operation such as a completed purchase, completed sale, inventory adjustment, or transaction cancellation.

**Related:** BR-026, BR-031, FR-056

---

# 10. Expense Rules

## BRL-056 — Expense Recording

Authorized users may record business expenses.

**Related:** BR-045, FR-057

---

## BRL-057 — Expense Category

Each expense shall have an expense category.

**Related:** BR-046, FR-058

---

## BRL-058 — Positive Expense Amount

Expense amounts shall be greater than zero.

**Related:** BR-045, FR-059

---

## BRL-059 — Expense Date

Each expense shall record its relevant date and time.

**Related:** BR-047, FR-060

---

## BRL-060 — Expense Does Not Affect Inventory

Recording an expense shall not modify product inventory.

**Related:** BR-045

---

# 11. Transaction Immutability Rules

## BRL-061 — Draft Transactions Are Editable

Draft sales and purchases may be edited by authorized users.

**Related:** BR-089, FR-098

---

## BRL-062 — Completed Transactions Are Immutable

Completed sales and purchases shall not be normally edited.

Their historical item quantities, prices, costs, totals, and business details shall remain unchanged.

**Related:** BR-089, FR-098, FR-089

---

## BRL-063 — Completed Transactions Are Not Deleted

Completed transactions shall not be physically deleted.

**Related:** BR-078, BR-082, BR-089

---

## BRL-064 — Cancellation Is Not Deletion

Cancellation shall preserve the original transaction and record the cancellation separately.

**Related:** BR-090, FR-099, FR-100

---

# 12. Transaction Cancellation Rules

## BRL-065 — Cancellation Eligibility

Only completed sales and purchases may be cancelled.

Draft transactions shall be handled through normal editing or deletion of the draft according to implementation rules.

Already cancelled transactions cannot be cancelled again.

**Related:** BR-090, FR-099

---

## BRL-066 — Cancellation Authorization

Transaction cancellation shall require appropriate authorization.

The exact role-permission matrix remains to be finalized.

**Related:** BR-090, BR-056, FR-099

---

## BRL-067 — Cancellation Reason

A cancellation shall require a reason.

**Related:** BR-090, FR-100

---

## BRL-068 — Cancellation Audit

A cancellation shall record:

* cancellation date/time;
* user performing the cancellation;
* cancellation reason;
* original transaction reference.

**Related:** BR-082, FR-100

---

## BRL-069 — Sale Cancellation Inventory Reversal

Cancelling a completed sale shall reverse the inventory decrease caused by the original sale.

**Related:** BR-090, BR-091, FR-101

---

## BRL-070 — Purchase Cancellation Inventory Reversal

Cancelling a completed purchase shall reverse the inventory increase caused by the original purchase.

The reversal shall only be permitted when the resulting inventory state satisfies the applicable inventory rules.

**Related:** BR-090, BR-091, FR-101

---

## BRL-071 — Sale Cancellation Financial Reversal

Cancelling a completed sale shall reverse the financial effect created by that sale.

For a credit sale, the applicable customer receivable shall be reversed.

For a cash sale, the applicable payment/financial effect shall be reversed according to the payment records and cancellation process.

**Related:** BR-090, FR-102

---

## BRL-072 — Purchase Cancellation Financial Reversal

Cancelling a completed purchase shall reverse the financial effect created by that purchase.

For a credit purchase, the applicable supplier payable shall be reversed.

For a cash purchase, the applicable payment/financial effect shall be reversed according to the payment records and cancellation process.

**Related:** BR-090, FR-102

---

## BRL-073 — Cancelled Transactions Excluded From Normal Totals

Cancelled transactions shall not be included in normal completed-sales, completed-purchases, inventory, or profitability totals.

Their historical existence shall remain available for audit purposes.

**Related:** BR-078, BR-089, BR-090

---

# 13. User and Access Rules

## BRL-074 — Authentication Required

Protected system functionality shall require an authenticated user.

**Related:** BR-054, FR-001–FR-004

---

## BRL-075 — V1 Business Roles

The V1 business roles are:

* Shop Owner
* Manager
* Cashier
* Warehouse Employee

The exact permission matrix shall be finalized before implementation.

**Related:** BR-053–BR-056, FR-063–FR-065

---

## BRL-076 — Role-Based Authorization

Users shall only perform operations permitted by their assigned role.

Authorization shall be enforced on the server side.

**Related:** BR-056, FR-065, NFR-003

---

## BRL-077 — Activity History

Important business actions shall be attributable to the user who performed them.

Examples include:

* creating transactions;
* completing transactions;
* cancelling transactions;
* recording payments;
* adjusting inventory;
* changing important business information.

**Related:** BR-057, BR-082, FR-066, FR-091

---

# 14. Reporting Rules

## BRL-078 — Completed Transactions as Official Data

Normal operational reports shall use completed transactions as the source of official sales and purchase activity.

Draft transactions shall be excluded.

Cancelled transactions shall be excluded from normal totals.

**Related:** BR-058–BR-067

---

## BRL-079 — Revenue

For reporting purposes:

```text
Revenue = applicable completed sales revenue
```

The treatment of discounts shall follow the finalized discount rules.

**Related:** BR-068, FR-067, FR-071

---

## BRL-080 — Cost of Goods Sold

COGS shall be calculated from the applicable purchase-cost information associated with sold products and the approved inventory-costing methodology.

**Related:** BR-062, BR-070

---

## BRL-081 — Gross Profit

```text
Gross Profit = Revenue − COGS
```

**Related:** BR-062, FR-071

---

## BRL-082 — Gross Margin

```text
Gross Margin =
Gross Profit / Revenue × 100
```

**Related:** BR-063, FR-072

---

## BRL-083 — Historical Data for Analytics

Completed historical transactions shall remain available for reporting and analytics.

**Related:** BR-078, BR-068–BR-077, FR-077–FR-086

---

# 15. Data Integrity Rules

## BRL-084 — Unique Transaction References

Major business transactions shall have unique identifiers/references.

**Related:** BR-080, FR-087

---

## BRL-085 — Transaction Dates

Business transactions shall preserve their relevant date/time information.

**Related:** BR-079, FR-088

---

## BRL-086 — Referential Integrity

Related records shall reference valid parent records.

Examples:

```text
Sale
 ↓
Sale Items
 ↓
Product
```

and:

```text
Purchase
 ↓
Purchase Items
 ↓
Product
```

**Related:** BR-081, FR-090

---

## BRL-087 — Historical Data Preservation

Changes to current master data shall not overwrite historical transaction data.

**Related:** BR-078, BR-082, FR-089

---

# 16. Backup and Recovery Rules

## BRL-088 — Local Backup

The system shall support backup of business data.

**Related:** BR-083, FR-092

---

## BRL-089 — Backup Recovery

A valid backup shall be usable to restore business data after an appropriate failure scenario.

**Related:** BR-084, FR-093, NFR-009

---

# 17. Operational Rules

## BRL-090 — Offline Operation

V1 shall operate without an Internet connection.

**Related:** BR-085, FR-094

---

## BRL-091 — Local Deployment

V1 shall operate using a locally hosted application and database.

**Related:** BR-086, FR-095

---

## BRL-092 — Browser-Based Access

Users shall access the application through a web browser.

**Related:** BR-087, FR-096

---

## BRL-093 — Future Extensibility

The system architecture shall preserve the ability to support future capabilities such as:

* multi-branch operation;
* remote access;
* mobile access;
* cloud deployment;
* external integrations.

These capabilities are outside V1 scope.

**Related:** BR-088, FR-097

---

# 18. Atomic Transaction Rules

## BRL-094 — Sale Completion Atomicity

Sale completion shall be treated as one business operation.

The sale, sale items, inventory changes, and applicable financial effects shall either all succeed or all fail.

**Related:** BR-016, BR-026, BR-081

---

## BRL-095 — Purchase Completion Atomicity

Purchase completion shall be treated as one business operation.

The purchase, purchase items, inventory changes, and applicable financial effects shall either all succeed or all fail.

**Related:** BR-008, BR-027, BR-081

---

## BRL-096 — Cancellation Atomicity

Transaction cancellation shall be treated as one business operation.

The cancellation record, inventory reversal, and applicable financial reversal shall either all succeed or all fail.

**Related:** BR-090, BR-091

---

# 19. Server-Side Enforcement

## BRL-097 — Business Rules Are Server-Enforced

Critical business rules shall be enforced on the server side.

Client-side validation may improve usability but shall not be the sole mechanism enforcing business constraints.

Examples include:

* sufficient inventory;
* transaction state;
* authorization;
* payment validation;
* cancellation eligibility;
* financial consistency.

**Related:** NFR-001, NFR-003

---

## BRL-098 — Database Integrity

The database shall enforce appropriate structural constraints such as:

* required fields;
* valid foreign-key relationships;
* unique identifiers;
* valid numeric values where applicable.

**Related:** BR-081, NFR-001

---

# 20. V1 Scope Boundaries

## BRL-099 — No Product Returns

V1 shall not support customer product returns or supplier product returns.

There shall be no V1 return workflow or return transaction type.

**Related:** Scope decision

---

## BRL-100 — No Product Refund Workflow

V1 shall not implement a product-return-driven refund workflow.

Transaction cancellation is separate from a product return and shall not be treated as a return mechanism.

**Related:** Scope decision

---

## BRL-101 — Single-Store V1

V1 is designed for a single store.

Multi-store or multi-branch operation is deferred to future versions.

**Related:** BR-088

---

## BRL-102 — No Multi-Tenancy in V1

V1 shall not implement multi-tenant architecture.

The design should not prevent future expansion to multiple stores or branches.

**Related:** BR-088

---

## BRL-103 — Arabic-First User Interface

The V1 user interface shall be Arabic-first and support right-to-left presentation.

User-facing labels and messages shall be presented in Arabic.

Source code, database identifiers, API identifiers, technical documentation, and Git history shall remain in English.

---

# 21. Calculated Balances

## BRL-104 — Customer Balance Is Calculated

Customer outstanding balances shall be calculated from applicable financial transactions and payments rather than maintained as an independently editable balance field.

**Related:** BR-024, BR-039, FR-017

---

## BRL-105 — Supplier Balance Is Calculated

Supplier outstanding balances shall be calculated from applicable financial transactions and payments rather than maintained as an independently editable balance field.

**Related:** BR-044, FR-022

---

# 22. Open Business Decisions

The following items remain intentionally unresolved and shall not be invented during implementation.

## OD-001 — Discount Mechanics

To be finalized:

* percentage or fixed;
* item-level or sale-level;
* maximum discount;
* authorization requirements;
* profitability restrictions.

---

## OD-002 — Inventory Costing Method

The inventory valuation and COGS methodology must be finalized.

---

## OD-003 — SKU/Barcode Behavior

The exact SKU/barcode workflow remains open.

---

## OD-004 — Payment Methods

The exact payment methods supported by the business remain open.

---

## OD-005 — Role Permission Matrix

The exact permissions for:

* Owner;
* Manager;
* Cashier;
* Warehouse Employee

must be finalized.

---

## OD-006 — Backup Schedule

The exact backup frequency, retention policy, and operational procedure remain open.

---

## OD-007 — Negative Inventory

Whether negative inventory is permitted remains open.

The default implementation assumption should be **not permitted** until explicitly approved otherwise.

---

# 23. Explicitly Removed From V1

The following are outside V1 scope:

* Customer returns
* Supplier returns
* Return transactions
* Return IDs
* Return-driven refunds
* Partial returns
* Product-return workflows

If these capabilities are required later, they shall be introduced as new requirements rather than implicitly added to V1.

---

# 24. Requirements Traceability

The intended traceability chain is:

```text
Business Requirement
        ↓
Functional Requirement
        ↓
Use Case
        ↓
Business Rule
        ↓
Database Entity
        ↓
Implementation
        ↓
Test Case
```

Example:

```text
BR-028
Completed sales must decrease inventory.

        ↓

FR-040
When a sale is completed, inventory shall decrease.

        ↓

UC-011
Complete Sale

        ↓

BRL-029
A completed sale decreases inventory.

        ↓

Database

Sale
SaleItem
Product.current_stock

        ↓

Test

TC-XXX
Verify inventory decreases after completed sale.
```

No `InventoryTransaction` table is required by this business rule for V1.

---

# 25. Final Business Rule Principles

The V1 system shall follow these fundamental principles:

1. Draft transactions do not affect official inventory or financial balances.
2. Completed transactions are immutable.
3. Completed transactions cannot be physically deleted.
4. Completed transactions may be cancelled by authorized users.
5. Cancellation preserves the original transaction.
6. Cancellation reverses applicable inventory effects.
7. Cancellation reverses applicable financial effects.
8. Historical transaction prices and costs remain unchanged.
9. Customer and supplier balances are calculated rather than directly edited.
10. Inventory changes must originate from authorized business operations.
11. Important business actions must be auditable.
12. Business operations must be atomic.
13. Critical rules must be enforced server-side.
14. V1 does not support product returns.
15. V1 operates locally and offline.
16. V1 is single-store.
17. The architecture preserves future expansion without implementing future functionality prematurely.

---

# 26. Validation Status

Before implementation, the following must be validated:

* [ ] Business rules reviewed against the BRD.
* [ ] Functional requirements reviewed against these rules.
* [ ] Role and permission matrix finalized.
* [ ] Discount mechanics finalized.
* [ ] Payment methods finalized.
* [ ] Inventory costing methodology finalized.
* [ ] Negative inventory policy finalized.
* [ ] Backup policy finalized.
* [ ] Database design updated for confirmed discount requirements.
* [ ] Use cases updated to match the final transaction lifecycle.
* [ ] Test cases mapped to business rules.

**Status:** Draft — ready for final cross-document traceability review.
