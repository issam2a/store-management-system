# Store Management & Business Analytics System

**Project Type:** Web-Based Store Management System

**Business Domain:** Retail / Hospitality Products

**Project Status:** Planning

**Document:** Project Charter

**Version:** 1.0

**Author:** Issam

**Date:** September 2026

---

# 1. Executive Summary

This project aims to design and develop a web-based Store Management and Business Analytics System for a hospitality retail shop.

The system will centralize the shop's day-to-day operations, including product management, purchasing, sales, inventory, customers, suppliers, payments, debts, returns, and expenses.

Beyond operational management, the system will capture structured transactional data that can be used to generate business reports and analytical insights.

Version 1 will operate locally on the shop's laptop without requiring Internet access. The architecture will be designed so that future versions can support additional devices and remote Internet access without requiring a fundamental redesign of the application.

---

# 2. Business Context

The target business is a retail shop specializing in hospitality-related products such as:

* Nuts and seeds
* Coffee
* Chocolate
* Sweets
* Dates
* Dried fruits
* Gift boxes
* Hospitality trays

The shop purchases products from multiple suppliers and sells products using different units of measurement, including kilograms, grams, pieces, boxes, and packages.

The business needs to manage both physical inventory and financial transactions while maintaining historical data that can later be analyzed to support business decisions.

---

# 3. Business Problem

The shop requires a centralized system for managing its operational and financial information.

Without a structured management system, the business may face difficulties such as:

* Inaccurate inventory information.
* Difficulty tracking purchases and sales.
* Difficulty monitoring customer debts.
* Difficulty monitoring supplier balances.
* Difficulty identifying profitable products.
* Difficulty tracking business expenses.
* Limited visibility into sales trends.
* Difficulty identifying slow-moving or low-stock products.
* Lack of reliable historical data for analysis.
* Dependence on manual calculations and records.

The project addresses these problems by providing a centralized application backed by a relational database.

---

# 4. Project Goal

The primary goal is to develop a reliable store management system that supports the shop's daily operations while creating a high-quality historical dataset for business analytics.

The system should allow authorized users to:

1. Manage products and categories.
2. Record purchases.
3. Record sales.
4. Track inventory.
5. Manage customers.
6. Manage suppliers.
7. Track payments and outstanding balances.
8. Process sales and purchase returns.
9. Record business expenses.
10. Generate operational and financial reports.
11. Analyze business performance.

---

# 5. Project Objectives

## 5.1 Operational Objectives

The system will:

* Centralize store data.
* Reduce manual data entry and calculations.
* Maintain accurate inventory balances.
* Track sales and purchases.
* Track customer and supplier balances.
* Record payments.
* Record returns.
* Record business expenses.
* Provide management reports.
* Maintain an auditable history of transactions.

## 5.2 Data and Analytics Objectives

The system will capture structured transactional data that can support:

* Revenue analysis.
* Gross profit analysis.
* Gross margin analysis.
* Product performance analysis.
* Customer analysis.
* Supplier analysis.
* Inventory analysis.
* Sales trend analysis.
* Historical price analysis.

The data model will be designed with future analytical requirements in mind.

---

# 6. Project Scope

## 6.1 In Scope

### Product Management

* Product creation.
* Product modification.
* Product categorization.
* Unit-of-measure management.
* Purchase price management.
* Selling price management.
* Minimum stock levels.
* Product identification/barcodes where applicable.

### Sales Management

* Sales invoice creation.
* Multiple products within a single sale.
* Cash sales.
* Credit sales.
* Payment recording.
* Discounts.
* Sales returns.
* Sales history.

### Purchase Management

* Supplier purchases.
* Purchase invoices.
* Multiple products within a purchase.
* Cash purchases.
* Credit purchases.
* Supplier payments.
* Purchase returns.
* Purchase history.

### Inventory Management

* Inventory tracking.
* Inventory movements.
* Stock increases from purchases.
* Stock decreases from sales.
* Stock increases from customer returns.
* Stock decreases from supplier returns.
* Stock adjustments.
* Damaged/lost inventory recording.
* Low-stock monitoring.
* Inventory valuation.

### Customer Management

* Customer records.
* Customer purchase history.
* Customer payments.
* Customer credit balances.
* Outstanding customer balances.

### Supplier Management

* Supplier records.
* Supplier purchase history.
* Supplier payments.
* Outstanding supplier balances.

### Expense Management

* Expense recording.
* Expense categorization.
* Expense history.
* Expense reporting.

### User Management

* User authentication.
* User accounts.
* User roles.
* Permission management.
* Activity/audit tracking.

### Reporting

The system will provide reports including:

* Daily sales.
* Monthly sales.
* Sales by product.
* Sales by category.
* Gross profit.
* Gross margin.
* Inventory status.
* Low-stock products.
* Customer balances.
* Supplier balances.
* Expenses.
* Product performance.

### Analytics

The system will support analysis such as:

* Top-selling products.
* Most profitable products.
* Product profitability.
* Sales trends.
* Inventory turnover.
* Slow-moving products.
* Customer purchasing behavior.
* Supplier purchasing patterns.
* Purchase price changes.

---

# 7. Out of Scope for Version 1

The following features are intentionally excluded from the first version:

* Internet-based remote access.
* Cloud hosting.
* Mobile application.
* Multiple store branches.
* Online payment gateways.
* Integration with external accounting systems.
* Automated purchasing from suppliers.
* AI-based forecasting.
* External third-party integrations unless required later.

These features may be considered in future releases.

---

# 8. Initial Deployment Model

Version 1 will run entirely on the shop's laptop.

The architecture will be:

```text
┌──────────────────────────┐
│       Web Browser        │
│          Chrome          │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│      Django Server       │
│       localhost          │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│       PostgreSQL         │
│        Database          │
└──────────────────────────┘
```

The system will not depend on an Internet connection for normal operation.

---

# 9. Planned Technology Stack

| Layer                 | Technology        |
| --------------------- | ----------------- |
| Backend               | Django            |
| Database              | PostgreSQL        |
| Frontend              | Django Templates  |
| UI Framework          | Bootstrap         |
| Data Visualization    | Chart.js          |
| Data Analysis         | Python / Pandas   |
| Business Intelligence | Power BI          |
| Version Control       | Git / GitHub      |
| Containerization      | Docker            |
| Future Remote Access  | Cloudflare Tunnel |

The technology stack may be adjusted during implementation if technical requirements justify a change.

---

# 10. High-Level System Architecture

The initial system will follow a layered architecture:

```text
┌──────────────────────────────┐
│       Presentation Layer     │
│      Django Templates        │
│          Bootstrap           │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       Application Layer      │
│           Django             │
│                              │
│ Products                     │
│ Sales                        │
│ Purchases                    │
│ Inventory                    │
│ Customers                    │
│ Suppliers                    │
│ Expenses                     │
│ Reports                      │
│ Users                        │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│          Data Layer          │
│         PostgreSQL           │
└──────────────────────────────┘
```

The architecture will maintain clear separation between the user interface, business logic, and data storage.

---

# 11. Stakeholders

## Primary Stakeholder

### Shop Owner

Responsibilities:

* Provide business requirements.
* Explain existing business processes.
* Validate workflows.
* Validate reports.
* Test the system.
* Provide feedback.
* Approve the final system.

## System Developer

Responsibilities:

* Requirements analysis.
* Business process analysis.
* System architecture.
* Database design.
* Application development.
* Data modeling.
* Testing.
* Documentation.
* Deployment.
* Analytics development.

## System Users

Potential users include:

* Owner
* Manager
* Cashier
* Warehouse employee

The exact permissions of each role will be defined during requirements analysis.

---

# 12. Success Criteria

The project will be considered successful when:

### Operational

* Products can be managed through the system.
* Purchases can be recorded accurately.
* Sales can be recorded accurately.
* Inventory is automatically updated by relevant transactions.
* Customer balances are tracked correctly.
* Supplier balances are tracked correctly.
* Returns can be processed correctly.
* Expenses can be recorded.
* Users can access functionality according to their permissions.

### Reporting

* Daily sales can be reported.
* Monthly sales can be reported.
* Gross profit can be calculated.
* Gross margin can be calculated.
* Inventory status can be reported.
* Customer and supplier balances can be reported.

### Analytics

* Product performance can be analyzed.
* Sales trends can be analyzed.
* Inventory performance can be analyzed.
* Customer purchasing behavior can be analyzed.
* Supplier purchasing patterns can be analyzed.

### Technical

* The system operates without Internet access.
* Business data is stored in PostgreSQL.
* The application is version-controlled using Git.
* The project is documented sufficiently for another developer to understand and deploy it.
* The architecture allows future expansion without major changes to the core business logic.

---

# 13. Future Scalability

The initial system will be intentionally designed so that the deployment environment can evolve.

### Version 1 — Local

```text
Browser
   ↓
Django
   ↓
PostgreSQL
```

### Future — Local Network

```text
Laptop / Phone
       ↓
    Wi-Fi
       ↓
    Django
       ↓
  PostgreSQL
```

### Future — Remote Access

```text
Phone / Computer
       ↓
    Internet
       ↓
Cloudflare Tunnel
       ↓
    Django
       ↓
  PostgreSQL
```

The objective is to change the deployment and networking layer without rewriting the core business functionality.

---

# 14. Data Strategy

A fundamental principle of the project is to treat operational transactions as a source of reliable business data.

The system will preserve historical transactional information rather than relying exclusively on manually maintained summary values.

The data will support two major purposes:

### Operational Use

```text
Sales
Purchases
Inventory
Payments
Customers
Suppliers
Expenses
```

### Analytical Use

```text
Revenue
Profit
Margins
Product Performance
Customer Behavior
Supplier Performance
Inventory Performance
Sales Trends
```

This separation will allow the same operational database to serve the store while providing a foundation for future analytical models and Business Intelligence dashboards.

---

# 15. Project Constraints

Initial constraints include:

* The first version must operate without Internet access.
* The system will initially run on one laptop.
* The application should not depend on cloud infrastructure.
* The system should use technologies that are practical to maintain.
* The database must preserve historical transaction data.
* The application should be designed for future expansion.

---

# 16. Assumptions

The project currently assumes that:

* The shop requires all major operational modules listed in the scope.
* Products may be sold using different units of measurement.
* The shop works with multiple suppliers.
* The shop has both cash and credit transactions.
* Customers may have outstanding balances.
* Suppliers may have outstanding balances.
* Products may be returned.
* Inventory adjustments may be required.
* Business expenses need to be recorded.
* Multiple users may eventually use the system.
* Historical transactional data will be valuable for analytics.

These assumptions will be validated during the detailed requirements phase.

---

# 17. Project Deliverables

The final project is expected to produce:

1. Requirements documentation.
2. Use case documentation.
3. System architecture documentation.
4. Entity Relationship Diagram (ERD).
5. PostgreSQL database schema.
6. Django web application.
7. Authentication and authorization system.
8. Inventory management system.
9. Sales and purchasing modules.
10. Customer and supplier management.
11. Expense management.
12. Operational reports.
13. Analytics dashboards.
14. Test documentation.
15. Deployment documentation.
16. GitHub repository.
17. Project README.
18. Portfolio case study.

---

# 18. Project Development Approach

The project will be developed incrementally.

The planned sequence is:

```text
Project Charter
      ↓
Business Requirements
      ↓
Functional Requirements
      ↓
Use Cases
      ↓
Business Rules
      ↓
System Architecture
      ↓
Database Design
      ↓
Django Implementation
      ↓
Testing
      ↓
Reports & Analytics
      ↓
Deployment
      ↓
Portfolio Documentation
```

Each stage should be completed and reviewed before moving to the next major stage.

---

# 19. Project Principle

The system will follow this core principle:

> **Build the operational system to capture reliable transactional data, then use that data to support better business decisions.**

The project is therefore both:

**A Store Management System**

and

**A Business Analytics Platform.**

This dual purpose is a core design consideration throughout the project.
