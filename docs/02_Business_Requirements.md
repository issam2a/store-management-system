# Store Management & Business Analytics System

## Business Requirements Document (BRD)

**Document ID:** BRD-001

**Version:** 1.0

**Status:** Draft

**Author:** Issam

**Date:** September 2026

**Related Document:** 01_Project_Charter.md

---

# 1. Purpose

This document defines the business requirements for the Store Management & Business Analytics System.

The purpose of the system is to provide a centralized solution for managing the shop's daily operations while capturing reliable transactional data for reporting and business analysis.

This document describes **what the business needs**, rather than how the system will be technically implemented.

Technical implementation details such as database tables, Django models, APIs, and application architecture will be defined in later documents.

---

# 2. Business Objectives

The system must support the following business objectives:

### BO-001 — Centralize Store Operations

Provide a single system for managing products, purchases, sales, inventory, customers, suppliers, payments, returns, and expenses.

### BO-002 — Improve Inventory Accuracy

Maintain an accurate record of product quantities based on business transactions and inventory adjustments.

### BO-003 — Improve Financial Visibility

Provide visibility into sales, purchases, payments, debts, expenses, and profitability.

### BO-004 — Reduce Manual Work

Reduce repetitive calculations and manual record keeping.

### BO-005 — Preserve Historical Data

Maintain historical transactional data that can be used for reporting and analysis.

### BO-006 — Support Business Decisions

Provide reports and analytics that help the owner understand sales, profitability, inventory, customers, and suppliers.

---

# 3. Stakeholders

## 3.1 Shop Owner

The shop owner is the primary business stakeholder.

The owner requires the ability to:

* Monitor business performance.
* Manage products.
* Review sales.
* Review purchases.
* Monitor inventory.
* Monitor customer debts.
* Monitor supplier balances.
* Record and review expenses.
* Analyze profitability.
* Access business reports.

---

## 3.2 Manager

A manager may perform operational activities on behalf of the owner.

Potential responsibilities include:

* Managing products.
* Managing sales.
* Managing purchases.
* Managing inventory.
* Managing customers and suppliers.
* Reviewing reports.

---

## 3.3 Cashier

The cashier is responsible primarily for sales transactions.

Potential responsibilities include:

* Creating sales.
* Recording customer payments.
* Processing customer returns.
* Viewing relevant customer information.

---

## 3.4 Warehouse Employee

The warehouse employee is responsible primarily for inventory-related activities.

Potential responsibilities include:

* Receiving purchased products.
* Checking inventory.
* Recording stock adjustments.
* Recording damaged products.
* Performing stock counts.

---

# 4. Business Requirements

## 4.1 Product Management

### BR-001 — Product Registration

The business requires the system to maintain a record for every product sold by the shop.

### BR-002 — Product Categories

The system shall allow authorized users to create, view, update, and deactivate product categories used to classify products.

Examples may include:

* Nuts
* Coffee
* Chocolate
* Sweets
* Dates
* Dried Fruits
* Gift Boxes
* Hospitality Trays

### BR-003 — Units of Measurement

The system shall allow authorized users to create, view, update, and deactivate units of measurement used to define how products are purchased, sold, and tracked in inventory.

Examples include:

* Kilogram
* Gram
* Piece
* Box
* Package

### BR-004 — Product Pricing

The business requires purchase and selling prices to be recorded for products.

### BR-005 — Price History

The business requires historical transaction data to preserve the prices used at the time of purchases and sales.

This is necessary because product prices may change over time.

### BR-006 — Minimum Stock Level

The business requires a minimum stock level to be defined for products where stock monitoring is required.

### BR-007 — Product Identification

The system should support product identifiers such as SKU or barcode where applicable.

---

# 5. Purchasing Requirements

## BR-008 — Supplier Purchases

The system must allow the business to record purchases from suppliers.

## BR-009 — Purchase Invoice

A purchase transaction must support multiple products within a single purchase.

## BR-010 — Purchase Quantity

The system must record the quantity purchased for each product.

## BR-011 — Purchase Price

The system must record the actual purchase price associated with each purchased product.

## BR-012 — Purchase Payment

The business must be able to record payments made to suppliers.

## BR-013 — Credit Purchases

The business must be able to record purchases that are not fully paid at the time of purchase.

## BR-014 — Supplier Balance

The system must allow the business to determine outstanding amounts owed to suppliers.



---

# 6. Sales Requirements

## BR-015 — Sales Transaction

The system must allow an authorized user to create a sales transaction.

## BR-016 — Multiple Products per Sale

A single sale must support multiple products.

## BR-017 — Sales Quantity

The system must record the quantity sold for each product.

## BR-018 — Selling Price

The system must preserve the selling price used at the time of the sale.

## BR-019 — Discounts

The system must support discounts on sales.

The exact discount rules will be defined during the functional requirements phase.

## BR-020 — Cash Sales

The system must support sales paid immediately.

## BR-021 — Credit Sales

The system must support sales where the customer does not pay the full amount immediately.

## BR-022 — Customer Payments

The system must allow payments toward outstanding customer balances to be recorded.

## BR-023 — Customer Balance

The system must allow the business to determine the amount owed by each credit customer.



---

# 7. Inventory Requirements

## BR-025 — Inventory Tracking

The system must maintain the current stock quantity of each inventory-controlled product.

## BR-026 — Purchase Inventory Movement

Completed purchases must increase the corresponding inventory quantities.

## BR-027 — Sales Inventory Movement

Completed sales must decrease the corresponding inventory quantities.

## BR-028 — Customer Return Movement

Accepted customer returns must increase inventory where the returned product is suitable for resale.


## BR-029 — Inventory Adjustment

Authorized users must be able to record inventory adjustments.

Examples include:

* Damaged products
* Lost products
* Stock-count corrections
* Other discrepancies

## BR-030 — Inventory History

The system must preserve the history of inventory movements.

## BR-031 — Low Stock

The system must identify products whose available quantity falls below their defined minimum stock level.

## BR-032 — Inventory Valuation

The system must support calculation of inventory value based on recorded inventory quantities and applicable cost information.

---

# 8. Customer Requirements

## BR-033 — Customer Registration

The system shall allow authorized users to create customer records for customers who purchase on credit or whose account balance needs to be tracked.

## BR-034 — Customer Information

The system shall support relevant information for account-tracked customers, such as:

* Name
* Phone number
* Contact information
* Account status

## BR-035 — Customer Purchase History

The system shall maintain the historical purchases associated with customers whose accounts are tracked.

## BR-036 — Customer Payment History

The system shall maintain payments made by customers whose accounts are tracked.

## BR-037 — Customer Debt

The system shall maintain and provide the outstanding balance of customers when credit transactions exist.

---

# 9. Supplier Requirements

## BR-038 — Supplier Registration

The system must allow authorized users to create supplier records.

## BR-039 — Supplier Information

The system should support relevant supplier information such as:

* Name
* Phone number
* Address
* Contact information

## BR-040 — Supplier Purchase History

The system must maintain historical purchases associated with each supplier.

## BR-041 — Supplier Payment History

The system must maintain payments made to suppliers.

## BR-042 — Supplier Debt

The system must provide the outstanding balance owed to each supplier.

---

# 10. Expense Requirements

## BR-043 — Expense Recording

The system must allow authorized users to record business expenses.

## BR-044 — Expense Categories

Expenses must be categorized.

Examples include:

* Rent
* Electricity
* Internet
* Salaries
* Transportation
* Packaging
* Maintenance
* Other operating expenses

## BR-045 — Expense History

The system must preserve historical expense records.

## BR-046 — Expense Reporting

The system must provide reports summarizing business expenses over selected periods.

---

# 11. Payment Requirements

## BR-047 — Payment Recording

The system must record payments associated with business transactions.

## BR-048 — Payment Method

The system should support the payment methods used by the shop.

Potential methods include:

* Cash
* Card
* Other methods used by the business

## BR-049 — Partial Payments

The system must support partial payments for credit transactions.

## BR-050 — Payment History

The system must preserve historical payment records.

---

# 12. User and Access Requirements

## BR-051 — User Accounts

The system must support individual user accounts.

## BR-052 — Authentication

Users must authenticate before accessing protected system functionality.

## BR-053 — User Roles

The system must support different user roles.

Potential roles include:

* Owner
* Manager
* Cashier
* Warehouse Employee

## BR-054 — Access Control

Users should only have access to functionality appropriate to their role.

## BR-055 — Activity History

The system should preserve information about important user actions.

---

# 13. Reporting Requirements

## BR-056 — Daily Sales Report

The system must provide a report showing sales for a selected day.

## BR-057 — Monthly Sales Report

The system must provide a report showing sales for a selected month.

## BR-058 — Product Sales Report

The system must provide sales information by product.

## BR-059 — Category Sales Report

The system must provide sales information by product category.

## BR-060 — Profit Report

The system must provide gross profit information.

## BR-061 — Gross Margin Report

The system must provide gross margin information.

## BR-062 — Inventory Report

The system must provide current inventory information.

## BR-063 — Customer Balance Report

The system must provide outstanding customer balances.

## BR-064 — Supplier Balance Report

The system must provide outstanding supplier balances.

## BR-065 — Expense Report

The system must provide expense information for selected periods.

---

# 14. Analytics Requirements

The system must preserve sufficient historical data to support business analysis.

## BR-066 — Revenue Analysis

The system must support analysis of revenue over time.

## BR-067 — Product Performance

The system must support analysis of product sales performance.

## BR-068 — Product Profitability

The system must support analysis of profit by product.

## BR-069 — Category Profitability

The system must support analysis of profit by product category.

## BR-070 — Sales Trends

The system must support analysis of sales trends over time.

## BR-071 — Inventory Performance

The system must support analysis of inventory movement and turnover.

## BR-072 — Slow-Moving Products

The system must support identification of products with low sales activity over a selected period.

## BR-073 — Customer Analysis

The system must support analysis of customer purchasing behavior.

## BR-074 — Supplier Analysis

The system must support analysis of purchasing patterns and supplier performance.

## BR-075 — Historical Price Analysis

The system must preserve historical purchase and selling prices to support price trend analysis.

---

# 15. Data Requirements

## BR-076 — Historical Transactions

The system must preserve completed business transactions rather than overwriting historical information.

## BR-077 — Transaction Dates

Transactions must record the date and time at which they occurred.

## BR-078 — Transaction References

Business transactions must have unique identifiers that allow them to be traced.

## BR-079 — Data Integrity

The system must maintain relationships between related business records.

For example:

```text
Sale
  ↓
Sale Items
  ↓
Products
```

and:

```text
Purchase
  ↓
Purchase Items
  ↓
Products
```

## BR-080 — Auditability

Important business operations must be traceable to the user who performed them.

---

# 16. Backup Requirements

## BR-081 — Local Backup

The system must support a mechanism for backing up the business database.

## BR-082 — Backup Recovery

The backup process must allow the database to be restored in the event of data loss or system failure.

The exact backup schedule and storage location will be defined during deployment planning.

---

# 17. Operational Constraints

## BR-083 — Offline Operation

Version 1 must operate without requiring Internet access.

## BR-084 — Local Deployment

Version 1 will run on the shop's laptop.

## BR-085 — Browser-Based Access

Users will interact with the application through a web browser.

## BR-086 — Future Expansion

The architecture should allow future support for:

* Local network access.
* Multiple devices.
* Remote Internet access.
* Cloud deployment.
* Additional branches.

---

## BR-087 — Transaction Immutability

Completed sales and purchases shall not be edited directly.


## BR-088 — Transaction Cancellation

Authorized users may cancel completed sales and purchases. Cancelled transactions shall remain in the system for audit purposes.

## BR-089 — Inventory Correction

Inventory discrepancies shall be corrected through inventory adjustments rather than by modifying completed transactions.


# 18. Business Metrics

The system should support the following key business metrics.

### Revenue

Total value of completed sales during a defined period.

### Cost of Goods Sold (COGS)

The cost associated with products sold during a defined period.

### Gross Profit

```text
Gross Profit = Revenue - COGS
```

### Gross Margin

```text
Gross Margin = Gross Profit / Revenue × 100
```

### Inventory Value

The estimated monetary value of inventory currently held by the business.

### Customer Outstanding Balance

The amount currently owed by a customer.

### Supplier Outstanding Balance

The amount currently owed to a supplier.

---

# 19. Requirements Traceability

Each business requirement has a unique identifier.

The identifiers will later be used to connect requirements to:

```text
Business Requirements
        ↓
Functional Requirements
        ↓
Use Cases
        ↓
Business Rules
        ↓
Database Design
        ↓
Implementation
        ↓
Test Cases
```

For example:

```text
BR-028
Sales must decrease inventory
        ↓
UC-003 Create Sale
        ↓
BRL-XXX Inventory Update Rule
        ↓
InventoryTransaction
        ↓
Test Case TC-XXX
```

This provides traceability throughout the project.

---

# 20. Requirements Status

All requirements in this document currently represent the assumed business scope for Version 1.

They should be reviewed and validated with the shop owner before implementation begins.

Changes discovered during stakeholder interviews should be documented through version updates rather than silently changing requirements.

---

# 21. Next Step

After the Business Requirements Document has been reviewed and approved, the next documentation stage is:

**Functional Requirements Specification (FRS).**

The FRS will translate the business requirements into detailed system behavior.

For example:

```text
Business Requirement:

BR-028
Completed sales must decrease inventory.

        ↓

Functional Requirement:

FR-XXX
When a user completes a sale, the system shall create
the appropriate inventory movement for every sale item
and update the available inventory quantity accordingly.
```


