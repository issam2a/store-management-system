# Store Management & Business Analytics System

## Functional Requirements Specification (FRS)

**Document ID:** FRS-001

**Version:** 1.0

**Status:** Draft

**Author:** Issam

**Date:** September 2026

**Related Documents:**

* `01_Project_Charter.md`
* `02_Business_Requirements.md`

---

# 1. Purpose

This document defines the functional and non-functional requirements of the Store Management & Business Analytics System.

The purpose of this document is to translate the business requirements into specific system behaviors that can be designed, implemented, and tested.

The requirements in this document describe **what the system shall do** without specifying the detailed implementation of the database, Django models, or user interface.

---

# 2. Requirement Identification

Each functional requirement has a unique identifier using the following format:

```text
FR-XXX
```

Where:

* `FR` = Functional Requirement
* `XXX` = Unique requirement number

Requirements are linked to their originating business requirements where applicable.

Example:

```text
BR-028
    ↓
FR-028.1
FR-028.2
FR-028.3
```

This provides traceability between business needs and system functionality.

---

# 3. User Authentication

## FR-001 — User Login

**Related:** BR-054

The system shall allow registered users to authenticate using valid credentials.

### Expected Behavior

1. User enters username and password.
2. System validates the credentials.
3. If valid, the system creates an authenticated session.
4. User is redirected to the appropriate application area.
5. If invalid, the system displays an authentication error.

---

## FR-002 — User Logout

The system shall allow an authenticated user to securely terminate their session.

---

## FR-003 — Unauthorized Access

The system shall prevent unauthenticated users from accessing protected application functionality.

---

## FR-004 — Session Management

The system shall manage authenticated user sessions and prevent unauthorized reuse of expired sessions.

---

# 4. Product Management

## FR-005 — Create Product

**Related:** BR-001

The system shall allow an authorized user to create a product.

The product shall contain the required product information defined by the business.

---

## FR-006 — Edit Product

**Related:** BR-001

The system shall allow authorized users to modify product information.

Historical transaction data shall not be modified as a result of changing the current product information.

---

## FR-007 — Product Categories

**Related:** BR-002

The system shall allow authorized users to create, view, update, and deactivate product categories. A category that is referenced by existing products or historical transactions shall not be physically deleted.

---

## FR-008 — Product Units

**Related:** BR-003

The system shall allow authorized users to create, view, update, and deactivate units of measurement. A unit that is referenced by existing products or historical transactions shall not be physically deleted.

Examples:

* Kilogram
* Gram
* Piece
* Box
* Package

---

## FR-009 — Product Pricing

**Related:** BR-004

The system shall allow authorized users to define and update the current/default purchase cost and selling price of each product through the Product Management module. These prices shall be automatically used as the default prices for new purchase and sale transactions. Changes to the current/default prices shall not modify prices stored in completed historical transactions.

---

## FR-010 — Historical Transaction Prices

**Related:** BR-005

When a product is included in a purchase or sale transaction, the system shall store the actual unit cost or selling price used for that transaction in the corresponding transaction item. The stored transaction price shall remain unchanged if the product's current/default price is subsequently modified.

---

## FR-011 — Minimum Stock Level

**Related:** BR-006

The system shall allow authorized users to define a minimum stock level for a product.

---

## FR-012 — Product Identifier

**Related:** BR-007

The system shall support a unique internal product identifier.

The system should also support SKU or barcode values where applicable.

---

# 5. Customer Management

## FR-013 — Create Customer

**Related:** BR-035

The system shall allow authorized users to create customer records for customers participating in credit transactions or requiring account tracking.

---

## FR-014 — Edit Customer

The system shall allow authorized users to update customer information.

---

## FR-015 — Customer Purchase History

**Related:** BR-037

The system shall allow authorized users to view the sales history associated with a customer.

---

## FR-016 — Customer Payment History

**Related:** BR-038

The system shall allow authorized users to view payments associated with a customer account.

---

## FR-017 — Customer Outstanding Balance

**Related:** BR-039

The system shall calculate and display the outstanding balance of a customer.

---

# 6. Supplier Management

## FR-018 — Create Supplier

**Related:** BR-040

The system shall allow authorized users to create supplier records.

---

## FR-019 — Edit Supplier

The system shall allow authorized users to update supplier information.

---

## FR-020 — Supplier Purchase History

**Related:** BR-042

The system shall allow authorized users to view purchases associated with a supplier.

---

## FR-021 — Supplier Payment History

**Related:** BR-043

The system shall allow authorized users to view payments made to suppliers.

---

## FR-022 — Supplier Outstanding Balance

**Related:** BR-044

The system shall calculate and display the outstanding balance owed to a supplier.

---

# 7. Purchase Management

## FR-023 — Create Purchase

**Related:** BR-008

The system shall allow an authorized user to create a purchase transaction associated with a supplier.

---

## FR-024 — Purchase Items

**Related:** BR-009

A purchase shall support multiple products.

Each purchase item shall contain information necessary to identify:

* Product
* Quantity
* Unit
* Purchase price
* Total amount

---

## FR-025 — Purchase Total

The system shall calculate the total value of a purchase from its individual purchase items.

```text
Purchase Total =
Σ (Quantity × Purchase Price)
```

---

## FR-026 — Purchase Payment

**Related:** BR-012

The system shall allow users to record payments associated with a purchase.

---

## FR-027 — Credit Purchase

**Related:** BR-013

The system shall support purchases where the amount paid is less than the total purchase amount.

The unpaid amount shall become part of the supplier's outstanding balance.

---

## FR-028 — Purchase Completion

The system shall allow an authorized user to complete a purchase transaction.

Only completed purchases shall affect inventory and financial balances.

---

## FR-029 — Purchase Inventory Update

**Related:** BR-027

When a purchase is completed, the system shall increase the inventory quantity of each applicable product.

---



# 8. Sales Management

## FR-030 — Create Sale

**Related:** BR-016

The system shall allow an authorized user to create a sales transaction.

---

## FR-031 — Sale Items

**Related:** BR-017

A sale shall support multiple products.

Each sale item shall contain:

* Product
* Quantity
* Unit
* Selling price
* Total amount

---

## FR-032 — Sale Total

**Related:** BR-016

The system shall calculate the total value of a sale from its individual sale items.

```text
Subtotal =
Σ (Quantity × Selling Price)
```

---

## FR-033 — Apply Discount

**Related:** BR-020

The system shall allow an authorized user to apply an approved discount to a sale.

The system shall record the discount separately from the original item prices.

---

## FR-034 — Cash Sale

**Related:** BR-021

The system shall support sales that are fully paid at the time of the transaction.

---

## FR-035 — Credit Sale

**Related:** BR-022

The system shall support sales where the customer pays less than the total sale amount.

The remaining amount shall become part of the customer's outstanding balance.

---

## FR-036 — Sale Completion

The system shall allow an authorized user to complete a sale.

Only completed sales shall affect inventory and financial records.

---

## FR-037 — Sale Inventory Update

**Related:** BR-028

When a sale is completed, the system shall decrease inventory for each applicable sale item.

---



# 9. Payment Management

## FR-038 — Record Payment

**Related:** BR-049

The system shall allow authorized users to record payments associated with customers or suppliers.

---

## FR-039 — Payment Method

**Related:** BR-050

The system shall allow a payment method to be recorded for each payment.

The supported methods shall be configurable according to the business requirements.

---

## FR-040 — Partial Payment

**Related:** BR-051

The system shall allow a payment to cover only part of an outstanding balance.

---

## FR-041 — Payment History

**Related:** BR-052

The system shall preserve payment records and allow authorized users to view payment history.

---

## FR-042 — Payment Validation

The system shall prevent a payment from being recorded with an invalid amount.

For example:

* Zero payment.
* Negative payment.
* Payment exceeding the allowed outstanding balance unless explicitly permitted by the business rules.

---

# 10. Inventory Management

## FR-043 — Current Inventory

**Related:** BR-026

The system shall provide the current available quantity for each inventory-controlled product.

---

## FR-044 — Inventory Movement

**Related:** BR-032

The system shall record inventory movements generated by business transactions.

Inventory movement types shall include, where applicable:

* Purchase
* Sale
* Customer Return
* Supplier Return
* Damage
* Loss
* Stock Adjustment

---

## FR-045 — Inventory Movement Reference

Each inventory movement shall be traceable to its originating business transaction or adjustment.

---

## FR-046 — Stock Adjustment

**Related:** BR-031

Authorized users shall be able to create inventory adjustments.

The system shall require an adjustment reason.

Examples:

* Damaged
* Lost
* Stock-count correction
* Other

---

## FR-047 — Low Stock Detection

**Related:** BR-033

The system shall identify products whose available quantity is below their configured minimum stock level.

---

## FR-048 — Inventory History

The system shall allow authorized users to review inventory movements over a selected period.

---

## FR-049 — Inventory Valuation

**Related:** BR-034

The system shall support calculation of the estimated value of current inventory using the applicable inventory cost methodology.

The exact costing methodology shall be defined in the business rules and database design stages.

---

## FR-050 — Inventory Integrity

The system shall prevent inventory quantities from being modified directly without generating an appropriate inventory transaction or authorized adjustment.

---

# 11. Expense Management

## FR-051 — Create Expense

**Related:** BR-045

The system shall allow authorized users to record a business expense.

---

## FR-052 — Expense Category

**Related:** BR-046

Each expense shall be associated with an expense category.

---

## FR-053 — Expense Amount

The system shall require a valid positive amount for each expense.

---

## FR-054 — Expense Date

The system shall record the date and time associated with each expense.

---

## FR-055 — Expense History

**Related:** BR-047

The system shall allow authorized users to view historical expenses.

---

## FR-056 — Expense Reporting

**Related:** BR-048

The system shall provide expense summaries for selected periods.

---

# 12. User Management

## FR-057 — Create User

**Related:** BR-053

An authorized administrator shall be able to create user accounts.

---

## FR-058 — Assign Role

**Related:** BR-055

An authorized administrator shall be able to assign an appropriate role to a user.

---

## FR-059 — Role-Based Access

**Related:** BR-056

The system shall restrict functionality according to the user's assigned role.

---

## FR-060 — User Activity

**Related:** BR-057

The system shall record important user actions.

Examples:

* Creating a sale.
* Completing a purchase.
* Processing a return.
* Adjusting inventory.
* Changing important business information.

---

# 13. Reporting

## FR-061 — Daily Sales Report

**Related:** BR-058

The system shall provide a report of sales for a selected day.

The report should include:

* Number of sales.
* Revenue.
* Discounts.
* Payments.
* Outstanding credit.

---

## FR-062 — Monthly Sales Report

**Related:** BR-059

The system shall provide sales information for a selected month.

---

## FR-063 — Product Sales Report

**Related:** BR-060

The system shall provide sales quantities and revenue by product.

---

## FR-064 — Category Sales Report

**Related:** BR-061

The system shall provide sales information grouped by product category.

---

## FR-065 — Gross Profit Report

**Related:** BR-062

The system shall provide gross profit for a selected period.

```text
Gross Profit = Revenue - COGS
```

---

## FR-066 — Gross Margin Report

**Related:** BR-063

The system shall provide gross margin for a selected period.

```text
Gross Margin =
Gross Profit / Revenue × 100
```

---

## FR-067 — Inventory Report

**Related:** BR-064

The system shall provide a report containing current inventory quantities and applicable stock information.

---

## FR-068 — Customer Balance Report

**Related:** BR-065

The system shall provide outstanding customer balances.

---

## FR-069 — Supplier Balance Report

**Related:** BR-066

The system shall provide outstanding supplier balances.

---

## FR-070 — Expense Report

**Related:** BR-067

The system shall provide expense summaries for selected periods.

---

# 14. Analytics

## FR-071 — Revenue Trend Analysis

**Related:** BR-068

The system shall provide data required to analyze revenue over time.

---

## FR-072 — Product Performance Analysis

**Related:** BR-069

The system shall provide data required to compare product sales performance.

---

## FR-073 — Product Profitability Analysis

**Related:** BR-070

The system shall provide data required to calculate and compare product profitability.

---

## FR-074 — Category Profitability Analysis

**Related:** BR-071

The system shall provide data required to analyze profitability by category.

---

## FR-075 — Sales Trend Analysis

**Related:** BR-072

The system shall provide historical sales data suitable for time-based analysis.

---

## FR-076 — Inventory Performance Analysis

**Related:** BR-073

The system shall provide data required to analyze inventory movement and turnover.

---

## FR-077 — Slow-Moving Products

**Related:** BR-074

The system shall provide data required to identify products with low sales activity during a selected period.

---

## FR-078 — Customer Analysis

**Related:** BR-075

The system shall provide data required to analyze customer purchasing behavior.

---

## FR-079 — Supplier Analysis

**Related:** BR-076

The system shall provide data required to analyze supplier purchasing patterns.

---

## FR-080 — Historical Price Analysis

**Related:** BR-077

The system shall preserve transaction-level purchase and selling prices so that historical price changes can be analyzed.

---

# 15. Data Management

## FR-081 — Transaction Identifiers

**Related:** BR-080

Each major business transaction shall have a unique identifier.

Examples:

* Sale ID
* Purchase ID
* Payment ID
* Return ID
* Expense ID

---

## FR-082 — Transaction Timestamp

**Related:** BR-079

Business transactions shall record their relevant date and time.

---

## FR-083 — Historical Transaction Preservation

**Related:** BR-078

Completed transactions shall not be overwritten when current master data changes.

For example, changing a product's current selling price shall not change the price recorded in historical sales.

---

## FR-084 — Referential Integrity

**Related:** BR-081

The system shall maintain valid relationships between related records.

For example:

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

---

# 16. Audit Trail

## FR-085 — Audit Logging

**Related:** BR-082

The system shall record important changes to business data.

The audit record should include, where applicable:

* User.
* Action.
* Entity.
* Record identifier.
* Date and time.
* Previous value.
* New value.

---

# 17. Backup and Recovery

## FR-086 — Database Backup

**Related:** BR-083

The system shall support database backup procedures.

---

## FR-087 — Database Restoration

**Related:** BR-084

The system shall support restoring business data from a valid backup.

---

# 18. Offline Operation

## FR-088 — Local Operation

**Related:** BR-085

Version 1 shall operate without an Internet connection.

---

## FR-089 — Local Database

**Related:** BR-086

The application shall use a locally hosted PostgreSQL database during Version 1.

---

## FR-090 — Browser Interface

**Related:** BR-087

Users shall interact with the system through a web browser.

---

# 19. Future Extensibility

## FR-091 — Modular Architecture

**Related:** BR-088

The system shall be organized into logical modules so that additional functionality can be introduced without requiring a complete rewrite.

Potential future modules include:

* Multi-branch management.
* Remote access.
* Mobile access.
* Cloud deployment.
* External integrations.

---

## FR-092 — Transaction Locking

The system shall prevent modification of completed sales and purchases.

---

## FR-093 — Transaction Cancellation

The system shall allow authorized users to cancel completed sales and purchases.

---

## FR-094 — Cancellation Audit Trail

When a transaction is cancelled, the system shall record the cancellation date and time, the user performing the cancellation, and the cancellation reason.

---
## FR-095 — Inventory Reversal on Cancellation

When a completed sale or purchase is cancelled, the system shall automatically reverse the inventory impact of the transaction.

---
## FR-094 — Financial Reversal on Cancellation

When a completed sale or purchase is cancelled, the system shall automatically reverse any related financial records according to the applicable business rules.

---
# 20. Non-Functional Requirements

Functional requirements describe **what the system does**.

The following requirements describe **how well the system should operate**.

---

## NFR-001 — Data Integrity

The system shall maintain the consistency and integrity of business data.

Transactions that would leave related records inconsistent shall not be completed.

---

## NFR-002 — Security

The system shall protect authenticated functionality from unauthorized access.

---

## NFR-003 — Authorization

The system shall enforce role-based permissions for protected operations.

---

## NFR-004 — Reliability

The system should reliably preserve completed transactions and prevent accidental data loss during normal operation.

---

## NFR-005 — Maintainability

The application should use modular components and clear separation of responsibilities to facilitate future maintenance.

---

## NFR-006 — Scalability

The architecture should allow the application to evolve from a single-laptop deployment to a multi-user or remotely accessible deployment.

---

## NFR-007 — Usability

Common store operations such as creating a sale or recording a purchase should require a practical number of steps and provide clear feedback to the user.

---

## NFR-008 — Performance

Normal operational actions should return results within an acceptable time under the expected workload of the shop.

Specific performance thresholds will be established after realistic workload requirements are known.

---

## NFR-009 — Recoverability

The system shall support restoration of business data from backups following a database failure.

---

## NFR-010 — Auditability

Important business operations shall be traceable to the user and time at which they occurred.

---

# 21. Transaction State Model

Business transactions such as sales and purchases shall have a defined lifecycle.

The initial model is:

```text
Draft
  ↓
Completed
  ↓
Returned / Partially Returned
```

A transaction may also be cancelled before completion according to the applicable business rules.

### Important Principle

Only transactions in the **Completed** state should affect official inventory and financial balances.

This prevents incomplete transactions from corrupting business data.

---

# 22. Data Flow Principles

The system shall treat business transactions as the source of operational changes.

For example:

### Purchase

```text
Purchase
    ↓
Purchase Items
    ↓
Inventory Movement (+)
    ↓
Inventory
```

### Sale

```text
Sale
    ↓
Sale Items
    ↓
Inventory Movement (-)
    ↓
Inventory
```

### Customer Payment

```text
Customer Payment
       ↓
Customer Account
       ↓
Outstanding Balance ↓
```

### Supplier Payment

```text
Supplier Payment
       ↓
Supplier Account
       ↓
Outstanding Balance ↓
```

This approach ensures that business state changes can be traced back to the transactions that caused them.

---

# 23. Requirements Traceability

The functional requirements will serve as the bridge between business requirements and later development artifacts.

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
Completed sales shall decrease inventory.

        ↓

UC-003
Complete Sale

        ↓

Business Rule
A completed sale generates an inventory decrease.

        ↓

Database
Sale
SaleItem
InventoryTransaction

        ↓

Test
TC-XXX
Verify inventory decreases after completed sale.
```

---

# 24. Requirement Priorities

Requirements will eventually be classified using:

### Must Have

Required for Version 1 to function.

### Should Have

Important but not essential for the first usable release.

### Could Have

Useful improvements that can be implemented later.

### Won't Have

Explicitly excluded from the current release.

The final priority classification will be reviewed before implementation begins.

---

# 25. Open Decisions

The following decisions must be finalized during the Business Rules and Database Design stages:

1. Exact inventory costing methodology.
2. Whether negative inventory is permitted.
3. Whether a sale can contain multiple payment methods.
4. Whether payments can exceed outstanding balances.
5. Exact return/refund rules.
6. Whether returned products automatically become available stock.
7. Exact discount permissions.
8. Whether historical prices are stored directly on transaction items.
9. Treatment of damaged and lost inventory.
10. Exact roles and permissions.
11. Whether transactions can be edited after completion.
12. Whether completed transactions can be cancelled or reversed.

These decisions should be documented rather than assumed during implementation.

---

# 26. Definition of Done for Functional Requirements

The functional requirements stage is considered complete when:

* Each major business requirement has corresponding functional requirements.
* Functional requirements are uniquely identified.
* Requirements are testable.
* Major system behaviors are defined.
* Transaction lifecycles are defined.
* Non-functional requirements are documented.
* Open business decisions are identified.
* Requirements can be traced to future use cases and test cases.

---

# 27. Next Step

After this document is reviewed, the next stage is:

**Use Case Specification.**

The use cases will describe how users interact with the system to accomplish specific business tasks.

Examples include:

```text
UC-001 Login
UC-002 Create Product
UC-003 Create Sale
UC-004 Complete Sale
UC-005 Create Purchase
UC-006 Complete Purchase
UC-007 Record Customer Payment
UC-008 Record Supplier Payment
UC-009 Process Sales Return
UC-010 Process Purchase Return
UC-011 Adjust Inventory
UC-012 Generate Sales Report
```

The use cases will then be used to refine the business rules before the database design begins.
