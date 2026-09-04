# 05 — System Architecture

## 1. Purpose

This document defines the system architecture of the Store Management & Business Analytics System.

The architecture describes the major software components, their responsibilities, interactions, technology choices, security model, data flow, and deployment approach.

The system is designed as a web application that initially runs locally on the store owner's laptop and can be extended in the future to support access from other devices without requiring a fundamental architectural redesign.

---

## 2. Architecture Overview

The system follows a layered web application architecture.

The initial architecture is:

```text
+----------------------+
|   User's Browser     |
|   HTML / CSS / JS    |
+----------+-----------+
           |
           | HTTP
           v
+----------------------+
|       Django         |
|  Web Application     |
|                      |
|  Views / Services    |
|  Forms / Validation  |
|  Authentication      |
+----------+-----------+
           |
           | Django ORM
           v
+----------------------+
|      PostgreSQL      |
|       Database       |
+----------------------+
```

The browser provides the user interface, Django handles application logic and web requests, and PostgreSQL stores persistent business data.

---

## 3. Architectural Style

The system uses a **layered architecture** based on Django's Model-View-Template (MVT) pattern.

### 3.1 Presentation Layer

Responsible for interaction with the user.

Technologies:

* Django Templates
* HTML
* CSS
* Bootstrap
* JavaScript
* Chart.js

Responsibilities:

* Display pages and forms.
* Collect user input.
* Display validation errors.
* Display transaction and business information.
* Display reports and dashboards.
* Provide an Arabic user interface.

The presentation layer shall not contain core business rules.

### 3.2 Application Layer

Responsible for coordinating business operations.

Implemented primarily using Django views and dedicated service logic where business operations require more complex processing.

Responsibilities:

* Process user requests.
* Validate business operations.
* Coordinate transactions.
* Enforce business rules.
* Manage transaction workflows.
* Coordinate inventory and financial updates.
* Control access to application functionality.

Complex business operations should be implemented in dedicated service functions or service modules rather than placing excessive business logic directly inside views.

### 3.3 Data Access Layer

Responsible for communication between the application and the database.

Technology:

* Django ORM

Responsibilities:

* Create and retrieve records.
* Update records.
* Enforce model-level validation where appropriate.
* Manage relationships between entities.
* Execute database queries.
* Provide transactional database operations.

Raw SQL may be used when required for specialized queries or performance-critical reporting, but normal application operations should use the Django ORM.

### 3.4 Database Layer

Technology:

* PostgreSQL

Responsibilities:

* Persistent storage.
* Referential integrity.
* Constraints.
* Transaction management.
* Indexing.
* Historical transaction storage.

PostgreSQL is the authoritative source of operational business data.

---

## 4. Technology Stack

| Component             | Technology       |
| --------------------- | ---------------- |
| Web Application       | Django           |
| Programming Language  | Python           |
| Database              | PostgreSQL       |
| ORM                   | Django ORM       |
| Frontend              | Django Templates |
| UI Framework          | Bootstrap        |
| Client-side Logic     | JavaScript       |
| Charts                | Chart.js         |
| Analytics             | Python / Pandas  |
| Business Intelligence | Power BI         |
| Version Control       | Git / GitHub     |

The system source code, database schema, technical documentation, and development artifacts shall use English.

The end-user interface shall be presented in Arabic.

---

## 5. Application Components

The Django application shall be organized into logical components according to business responsibilities.

The initial components are:

```text
Authentication
Product Management
Supplier Management
Customer Management
Purchasing
Sales
Payments
Inventory
Expenses
Reporting
User Management
Audit
```

These components may be implemented as separate Django apps where separation provides a clear architectural benefit.

The system should avoid unnecessary fragmentation into Django apps when the resulting separation does not provide meaningful maintainability or functional boundaries.

---

## 6. Authentication and Authorization

The system shall use Django's built-in authentication framework.

### 6.1 Authentication

Django Authentication shall be responsible for:

* User login.
* Password management.
* Session management.
* Authentication status.
* Account activation status.

Passwords shall never be stored as plain text.

### 6.2 Authorization

Access to system functionality shall be controlled according to user roles and permissions.

Initial roles are:

* Owner
* Cashier
* Administrator

Permissions shall determine which operations each role can perform.

Examples include:

* Creating sales.
* Completing sales.
* Creating purchases.
* Completing purchases.
* Recording payments.
* Managing products.
* Managing users.
* Cancelling transactions.
* Generating reports.

Authorization shall be enforced on the server side. Hiding a UI element alone shall not be considered sufficient authorization.

---

## 7. Internationalization and Language

The system shall support an **Arabic-first user interface** because the primary end user is Arabic-speaking.

### 7.1 User Interface Language

* All user-facing interface text shall be presented in Arabic.
* Navigation menus, buttons, forms, validation messages, notifications, and reports displayed within the application shall use Arabic.
* The interface shall support **Right-to-Left (RTL)** layout.
* Arabic labels and messages shall be managed separately from application logic to support future language expansion.

### 7.2 Technical Language

The following shall remain in English:

* Source code
* Variable and function names
* Database table and column names
* API endpoints
* Git commits
* Technical documentation
* Internal system identifiers

### 7.3 Future Language Support

The architecture shall allow additional languages to be introduced in the future without requiring changes to the underlying business logic or database structure.

The initial release shall prioritize Arabic and does not require a language-selection feature unless a future business requirement is introduced.


## 8. Business Transaction Processing

Business transactions that affect multiple records shall be processed using database transactions.

Examples include:

### Completing a Sale

```text
Complete Sale
     |
     +--> Validate Sale
     |
     +--> Verify Inventory
     |
     +--> Decrease Inventory
     |
     +--> Record Cash Payment
     |        OR
     +--> Create Customer Receivable
     |
     +--> Change Sale Status
     |
     +--> Record Completion Information
     |
     +--> Commit Transaction
```

### Completing a Purchase

```text
Complete Purchase
     |
     +--> Validate Purchase
     |
     +--> Increase Inventory
     |
     +--> Record Cash Payment
     |        OR
     +--> Create Supplier Payable
     |
     +--> Change Purchase Status
     |
     +--> Record Completion Information
     |
     +--> Commit Transaction
```

If any required operation fails, the database transaction shall be rolled back to prevent partially completed business transactions.

---

## 9. Inventory Architecture

Inventory quantity shall be maintained as part of the operational product/inventory data.

Inventory changes shall occur through controlled business operations.

The primary inventory-affecting operations are:

* Completed Purchase → Increase stock
* Completed Sale → Decrease stock
* Inventory Adjustment → Increase or decrease stock
* Cancelled Purchase → Reverse purchase inventory movement
* Cancelled Sale → Reverse sale inventory movement

Draft transactions shall not affect inventory.

Inventory operations shall be executed atomically with the transaction that caused the inventory change.

---

## 10. Financial Architecture

The system shall distinguish between:

### Immediate Payments

Payments associated with cash transactions.

Examples:

* Cash sale
* Cash purchase

### Credit Transactions

Transactions that create an outstanding balance.

Examples:

* Credit sale → Customer receivable
* Credit purchase → Supplier payable

### Later Payments

Payments used to settle previously created balances.

Examples:

* Customer Payment → Reduces customer receivable
* Supplier Payment → Reduces supplier payable

This separation prevents the original transaction and later settlement payment from being recorded as the same business event.

---

## 11. Historical Data Protection

Completed transactions shall preserve the actual values used when the transaction occurred.

For example:

```text
Product Current Selling Price
        $25
          |
          v
Sale Item
Unit Price = $25
```

If the product's current selling price later changes:

```text
Product Current Selling Price
        $27
```

the historical sale remains:

```text
Sale Item
Unit Price = $25
```

The same principle applies to purchase unit costs.

Completed transaction records shall not depend on the current product price for historical reporting.

---

## 12. Transaction Lifecycle

The system shall use explicit transaction states.

### Sale and Purchase Lifecycle

```text
Draft
  |
  v
Completed
  |
  v
Cancelled
```

### Draft

* Can be edited.
* Does not affect inventory.
* Does not create final financial effects.

### Completed

* Cannot be edited through normal transaction editing.
* Affects inventory.
* Creates the applicable payment or receivable/payable.
* Becomes part of operational reporting.

### Cancelled

* Cannot be completed again.
* Remains stored in the database.
* Original transaction information is preserved.
* Applicable inventory and financial effects are reversed.
* Cancellation information is retained for audit purposes.

---

## 13. Audit Architecture

The system shall maintain audit information for important business operations.

Relevant records shall include information such as:

* Created date and time
* Created by user
* Updated date and time
* Updated by user
* Completed date and time
* Completed by user
* Cancelled date and time
* Cancelled by user
* Cancellation reason

Audit information shall allow the business to determine who performed an operation and when it occurred.

---

## 14. Reporting Architecture

Operational reports shall obtain their data from PostgreSQL through Django.

The system shall support reports such as:

* Sales reports
* Inventory reports
* Customer balances
* Supplier balances
* Payment history
* Expense reports

For portfolio analytics, PostgreSQL data may also be extracted and analyzed using Python/Pandas and Power BI.

The operational application and analytical workflow should remain logically separated so that analytical processing does not compromise transactional operations.

---

## 15. Data Flow

A typical sale follows this flow:

```text
User
  |
  v
Browser
  |
  v
Django View
  |
  v
Business Logic
  |
  +----> Validate Sale
  |
  +----> PostgreSQL
  |          |
  |          +--> Sale
  |          +--> Sale Items
  |          +--> Inventory
  |          +--> Payment / Customer Balance
  |
  v
Response
  |
  v
Browser
```

A typical report follows:

```text
User
  |
  v
Browser
  |
  v
Django
  |
  v
PostgreSQL
  |
  v
Query / Aggregation
  |
  v
Report
  |
  v
Browser
```

---

## 16. Deployment Architecture

### 16.1 Initial Deployment

The first release shall be deployed on the shop owner's laptop.

The application shall be containerized using Docker to provide a consistent and portable runtime environment.

The deployment shall use Docker Compose to manage the application and database services.

The initial deployment architecture shall be:

```text
Shop Owner's Laptop
        |
        | Web Browser
        v
+---------------------------+
|      Docker Desktop       |
|                           |
|  +---------------------+  |
|  | Django Application  |  |
|  |     Container       |  |
|  +----------+----------+  |
|             |             |
|       Docker Network      |
|             |             |
|  +----------v----------+  |
|  |    PostgreSQL       |  |
|  |     Container       |  |
|  +---------------------+  |
|                           |
+---------------------------+

The application shall be accessed through the local machine using a browser.

### 16.2 Future Deployment

The architecture shall allow future access from additional devices.

Potential future architecture:

```text
Laptop / Phone / PC
        |
        v
   Local Network
        |
        v
      Django
        |
        v
    PostgreSQL
```

Future Internet access may be introduced using an appropriate secure deployment mechanism without redesigning the core business logic or database model.

---

## 17. Security Considerations

The system shall:

* Require authentication for protected functionality.
* Enforce authorization on the server.
* Hash user passwords using Django's authentication system.
* Protect against Cross-Site Request Forgery (CSRF).
* Validate user input.
* Use parameterized database operations through the Django ORM.
* Prevent unauthorized modification of completed transactions.
* Preserve audit information for sensitive operations.
* Restrict transaction cancellation to authorized users.
* Protect database credentials from exposure in source code.

Production secrets and credentials shall be stored outside the source code.

---

## 18. Non-Functional Architecture Considerations

### 18.1 Maintainability

The application shall use clear separation of responsibilities and consistent project structure.

### 18.2 Reliability

Critical business operations shall use atomic database transactions to prevent inconsistent data.

### 18.3 Scalability

The initial system is designed for a single store and local deployment but should allow future deployment on a local network or server without requiring major changes to the business domain model.

### 18.4 Usability

The end-user interface shall be designed primarily for Arabic-speaking users and optimized for straightforward daily store operations.

### 18.5 Extensibility

The architecture should allow future additions such as:

* Barcode scanning
* Additional reports
* More user roles
* Local network access
* Remote access
* Additional stores
* Advanced analytics

Future functionality shall be introduced only when justified by business requirements.

---

## 19. Architectural Principles

The following principles shall guide implementation:

1. Business rules shall be enforced on the server side.
2. Database integrity shall not depend solely on application-level validation.
3. Critical multi-step operations shall be atomic.
4. Historical transaction values shall be immutable after completion.
5. Draft transactions shall not affect inventory or finalized financial balances.
6. Completed transactions shall not be physically deleted.
7. Cancellation shall preserve historical information and reverse applicable effects.
8. Authentication and authorization shall be handled centrally.
9. Operational data and analytical processing shall remain logically separated.
10. The architecture shall remain simple enough to maintain as a small-business system.
