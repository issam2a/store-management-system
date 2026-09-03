# 04 — Use Case Specification

## 1. Purpose

This document defines the use cases of the Store Management & Business Analytics System. It describes how users interact with the system to perform business operations.

## 2. Actors

### 2.1 Owner

### 2.2 Cashier

### 2.3 Administrator

## 3. Use Case Index

| ID | Use Case | Primary Actor |
|---|---|---|
| UC-001 | Login | All Users |
| UC-002 | Create Product | Owner / Authorized User |
| UC-003 | Manage Product Categories | Owner / Authorized User |
| UC-004 | Manage Units | Owner / Authorized User |
| UC-005 | Update Product | Owner / Authorized User |
| UC-006 | Create Supplier | Owner |
| UC-007 | Create Customer | Owner / Cashier |
| UC-008 | Create Purchase | Owner / Cashier |
| UC-009 | Complete Purchase | Owner / Cashier |
| UC-010 | Create Purchase Return | Owner |
| UC-011 | Create Sale | Owner / Cashier |
| UC-012 | Complete Sale | Owner / Cashier |
| UC-013 | Create Sale Return | Owner |
| UC-014 | Record Customer Payment | Owner / Cashier |
| UC-015 | Record Supplier Payment | Owner / Cashier |
| UC-016 | Create Inventory Adjustment | Owner |
| UC-017 | Record Expense | Owner |
| UC-018 | Generate Sales Report | Owner |
| UC-019 | Generate Inventory Report | Owner |
| UC-020 | Manage Users | Administrator |

## 4. Use Case Specifications

---

## UC-001 — Login

### Goal

Allow an authorized user to securely access the system according to their assigned permissions.

### Primary Actor

Owner / Cashier / Administrator

### Preconditions

- The user has an active account.
- The user has valid login credentials.
- The system is available.

### Main Flow

1. The user opens the system.
2. The system displays the login screen.
3. The user enters their username and password.
4. The user submits the login form.
5. The system validates the credentials.
6. The system authenticates the user.
7. The system identifies the user's assigned role and permissions.
8. The system redirects the user to the appropriate dashboard.

### Alternate Flows

#### A1 — Invalid Credentials

1. The user enters an incorrect username or password.
2. The system rejects the login attempt.
3. The system displays an error message.
4. The user may attempt to log in again.


#### A2 — Inactive Account

1. The user enters valid credentials for an inactive account.
2. The system rejects the login attempt.
3. The system informs the user that the account is inactive.


### Postconditions

- The user is authenticated if valid credentials are provided.
- The user's role and permissions are loaded.
- The user's access is restricted according to their permissions.

### Related Requirements

- BR-053 — User Accounts
- BR-056 — Access Control
- FR-001 — User Authentication
- FR-002 — Role-Based Access
---

## UC-002 — Create Product

### Goal

Allow an authorized user to register a new product in the system with the information required for purchasing, selling, inventory management, and reporting.

### Primary Actor

Owner / Authorized User

### Preconditions

- The user is authenticated.
- The user has permission to create products.
- The system contains the product categories and units needed to create the product.

### Main Flow

1. The user opens the Product Management module.
2. The user selects "Create Product".
3. The system displays the product creation form.
4. The user enters the product name.
5. The user selects the product category.
6. The user selects the unit of measurement.
7. The user enters the current/default purchase cost.
8. The user enters the current/default selling price.
9. The user enters the minimum stock level.
10. The user submits the form.
11. The system validates the entered information.
12. The system creates the product.
13. The system assigns a unique product identifier.
14. The system records the product creation date and time.
15. The system displays a confirmation message.


### Alternate Flows

#### A1 — Missing Required Information

1. The user submits the form with one or more required fields missing.
2. The system rejects the submission.
3. The system identifies the missing information.
4. The user provides the required information and submits the form again.

#### A2 — Invalid Price

1. The user enters an invalid purchase cost or selling price.
2. The system rejects the entered value.
3. The system displays an appropriate validation message.
4. The user corrects the value and submits the form again.

#### A3 — Duplicate Product

1. The user enters information that matches an existing product according to the system's uniqueness rules.
2. The system warns the user that a similar or duplicate product already exists.
3. The user may review the existing product or correct the entered information.


### Postconditions

- A new product record exists in the system.
- The product has a unique identifier.
- The product's current/default purchase cost and selling price are stored.
- The product's category and unit are stored.
- The product's minimum stock level is stored.
- The product is available for future purchase and sale transactions.
- The product creation event is recorded for audit purposes.


### Related Requirements

- BR-001 — Product Registration
- BR-002 — Product Categories
- BR-003 — Units
- BR-004 — Pricing
- BR-006 — Minimum Stock
- BR-007 — Product Identifier
- BR-079 — Transaction Timestamps
- BR-081 — Data Integrity
- BR-082 — Auditability
- FR-005 — Create Product
- FR-007 — Product Categories
- FR-008 — Units
- FR-009 — Product Pricing
---

## UC-003 — Manage Product Categories

### Goal

Allow authorized users to manage the product categories used to classify products.

### Primary Actor

Owner / Authorized User

### Preconditions

- The user is authenticated.
- The user has permission to manage product categories.

### Main Flow

1. The user opens the Product Management module.
2. The user opens Category Management.
3. The system displays the existing product categories.
4. The user selects an action such as creating, viewing, updating, or deactivating a category.
5. The system performs the selected action after validating the request.
6. The system displays the updated category information.

### Alternate Flows

#### A1 — Create Category

1. The user selects "Create Category".
2. The user enters the category name.
3. The system validates the category name.
4. The system creates the category.
5. The new category becomes available for assigning to products.

#### A2 — Duplicate Category

1. The user enters a category name that already exists.
2. The system rejects the creation request.
3. The system informs the user that the category already exists.

#### A3 — Update Category

1. The user selects an existing category.
2. The user changes the category information.
3. The system validates the changes.
4. The system saves the updated category.

#### A4 — Deactivate Category

1. The user selects an active category.
2. The user chooses to deactivate it.
3. The system checks whether the category is referenced by existing products or historical records.
4. The system marks the category as inactive.
5. The category is no longer available for new product assignments.

### Postconditions

- A new category may be created.
- An existing category may be updated.
- A category may be deactivated without removing historical references.
- Active categories are available when creating or updating products.

### Related Requirements

- BR-002 — Product Categories
- BR-081 — Data Integrity
- BR-082 — Auditability
- FR-007 — Manage Product Categories


## UC-004 — Manage Units

### Goal

Allow authorized users to manage the units of measurement used by products.

### Primary Actor

Owner / Authorized User

### Preconditions

- The user is authenticated.
- The user has permission to manage units.

### Main Flow

1. The user opens the Product Management module.
2. The user opens Unit Management.
3. The system displays the existing units of measurement.
4. The user selects an action such as creating, viewing, updating, or deactivating a unit.
5. The system performs the selected action after validating the request.
6. The system displays the updated unit information.

### Alternate Flows

#### A1 — Create Unit

1. The user selects "Create Unit".
2. The user enters the unit name.
3. The system validates the unit name.
4. The system creates the unit.
5. The new unit becomes available for assigning to products.

#### A2 — Duplicate Unit

1. The user enters a unit name that already exists.
2. The system rejects the creation request.
3. The system informs the user that the unit already exists.

#### A3 — Update Unit

1. The user selects an existing unit.
2. The user changes the unit information.
3. The system validates the changes.
4. The system saves the updated unit.

#### A4 — Deactivate Unit

1. The user selects an active unit.
2. The user chooses to deactivate it.
3. The system checks whether the unit is referenced by existing products or historical records.
4. The system marks the unit as inactive.
5. The unit is no longer available for new product assignments.

### Postconditions

- A new unit may be created.
- An existing unit may be updated.
- A unit may be deactivated without removing historical references.
- Active units are available when creating or updating products.

### Related Requirements

- BR-003 — Units of Measurement
- BR-081 — Data Integrity
- BR-082 — Auditability
- FR-008 — Manage Units


## UC-005 — Update Product

### Goal

Allow an authorized user to update an existing product's information, including its current/default prices and minimum stock level, while preserving historical transaction data.

### Primary Actor

Owner / Authorized User

### Preconditions

* The user is authenticated.
* The user has permission to update products.
* The product already exists in the system.
* The product categories and units required for the update are available.

### Main Flow

1. The user opens the Product Management module.
2. The user searches for or selects an existing product.
3. The system displays the product's current information.
4. The user selects "Edit Product".
5. The user modifies the required product information.
6. The user may update:

   * Product name
   * Product category
   * Unit of measurement
   * Current/default purchase cost
   * Current/default selling price
   * Minimum stock level
7. The user submits the changes.
8. The system validates the entered information.
9. The system saves the updated product information.
10. The system records the date and time of the update.
11. The system records the user who performed the update.
12. The system displays a confirmation message.

### Alternate Flows

#### A1 — Product Not Found

1. The user searches for a product that does not exist.
2. The system displays a "Product not found" message.
3. The user searches again or cancels the operation.

#### A2 — Missing Required Information

1. The user submits the form with required information missing.
2. The system rejects the update.
3. The system identifies the missing information.
4. The user corrects the information and resubmits.

#### A3 — Invalid Price

1. The user enters an invalid purchase cost or selling price.
2. The system rejects the update.
3. The system displays the applicable validation message.
4. The user corrects the value and resubmits.

#### A4 — Duplicate Product Information

1. The user changes product information in a way that conflicts with an existing product according to the system's uniqueness rules.
2. The system rejects the update.
3. The system informs the user of the conflict.
4. The user corrects the information and resubmits.

#### A5 — Historical Transactions Exist

1. The product has existing purchase or sale transactions.
2. The user changes the current/default purchase cost or selling price.
3. The system updates the product's current/default price.
4. The system does not modify prices or costs stored in completed historical transactions.

### Postconditions

* The product information is updated successfully.
* The product's current/default purchase cost and selling price reflect the latest values.
* The minimum stock level reflects the latest value.
* Historical transaction prices and costs remain unchanged.
* The update event is recorded for audit purposes.

### Related Requirements

* BR-001 — Product Registration
* BR-004 — Product Pricing
* BR-005 — Price History
* BR-006 — Minimum Stock Level
* BR-081 — Data Integrity
* BR-082 — Auditability
* FR-005 — Manage Products
* FR-009 — Manage Product Prices
* FR-010 — Preserve Historical Transaction Prices


## UC-006 — Create Supplier

### Goal

Allow an authorized user to register a supplier in the system so that supplier information, purchases, supplier balances, payments, and supplier-related transactions can be tracked.

### Primary Actor

Owner

### Preconditions

* The user is authenticated.
* The user has permission to create suppliers.

### Main Flow

1. The user opens the Supplier Management module.
2. The user selects "Create Supplier".
3. The system displays the supplier creation form.
4. The user enters the supplier's required information.
5. The user submits the form.
6. The system validates the entered information.
7. The system creates the supplier record.
8. The system assigns a unique supplier identifier.
9. The system records the supplier creation date and time.
10. The system records the user who created the supplier.
11. The system displays a confirmation message.

### Alternate Flows

#### A1 — Missing Required Information

1. The user submits the form with required information missing.
2. The system rejects the creation request.
3. The system identifies the missing information.
4. The user provides the required information and resubmits.

#### A2 — Duplicate Supplier

1. The user enters supplier information that conflicts with an existing supplier according to the system's uniqueness rules.
2. The system rejects the creation request.
3. The system informs the user that the supplier may already exist.
4. The user reviews the existing supplier or corrects the information.

#### A3 — Invalid Supplier Information

1. The user enters invalid information, such as an invalid phone number or other field with a defined format.
2. The system rejects the creation request.
3. The system displays the applicable validation message.
4. The user corrects the information and resubmits.

### Postconditions

* A new supplier record exists in the system.
* The supplier has a unique identifier.
* The supplier is available for purchase transactions.
* Supplier information can be used to track purchases, payments, and outstanding balances.
* The supplier creation event is recorded for audit purposes.

### Related Requirements

* BR-040 — Supplier Registration
* BR-041 — Supplier Information
* BR-042 — Supplier Management
* FR-018 — Create Supplier
* FR-019 — Manage Supplier Information
---

## UC-008 — Create Purchase

### Goal

### Primary Actor

### Preconditions

### Main Flow

1. 
2. 
3. 

### Alternate Flows

#### A1 —

1. 

### Postconditions

### Related Requirements

---

## UC-009 — Complete Purchase

### Goal

### Primary Actor

### Preconditions

### Main Flow

1. 
2. 
3. 

### Alternate Flows

#### A1 —

1. 

### Postconditions

### Related Requirements

---

## UC-010 — Create Purchase Return

### Goal

### Primary Actor

### Preconditions

### Main Flow

1. 
2. 
3. 

### Alternate Flows

#### A1 —

1. 

### Postconditions

### Related Requirements

---

## UC-011— Create Sale

### Goal

### Primary Actor

### Preconditions

### Main Flow

1. 
2. 
3. 

### Alternate Flows

#### A1 —

1. 

### Postconditions

### Related Requirements

---

## UC-012 — Complete Sale

### Goal

### Primary Actor

### Preconditions

### Main Flow

1. 
2. 
3. 

### Alternate Flows

#### A1 — Credit Sale

1. 

#### A2 — Insufficient Stock

1. 

### Postconditions

### Related Requirements

---

## UC-013 — Create Sale Return

### Goal

### Primary Actor

### Preconditions

### Main Flow

1. 
2. 
3. 

### Alternate Flows

#### A1 —

1. 

### Postconditions

### Related Requirements

---

## UC-014 — Record Customer Payment

### Goal

### Primary Actor

### Preconditions

### Main Flow

1. 
2. 
3. 

### Alternate Flows

#### A1 —

1. 

### Postconditions

### Related Requirements

---

## UC-015 — Record Supplier Payment

### Goal

### Primary Actor

### Preconditions

### Main Flow

1. 
2. 
3. 

### Alternate Flows

#### A1 —

1. 

### Postconditions

### Related Requirements

---

## UC-016 — Create Inventory Adjustment

### Goal

### Primary Actor

### Preconditions

### Main Flow

1. 
2. 
3. 

### Alternate Flows

#### A1 —

1. 

### Postconditions

### Related Requirements

---

## UC-017 — Record Expense

### Goal

### Primary Actor

### Preconditions

### Main Flow

1. 
2. 
3. 

### Alternate Flows

#### A1 —

1. 

### Postconditions

### Related Requirements

---

## UC-018 — Generate Sales Report

### Goal

### Primary Actor

### Preconditions

### Main Flow

1. 
2. 
3. 

### Alternate Flows

#### A1 —

1. 

### Postconditions

### Related Requirements

---

## UC-019 — Generate Inventory Report

### Goal

### Primary Actor

### Preconditions

### Main Flow

1. 
2. 
3. 

### Alternate Flows

#### A1 —

1. 

### Postconditions

### Related Requirements

---

## UC-020 — Manage Users

### Goal

### Primary Actor

### Preconditions

### Main Flow

1. 
2. 
3. 

### Alternate Flows

#### A1 —

1. 

### Postconditions
    
### Related Requirements

---

## 5. Use Case Relationships

### 5.1 Sales

### 5.2 Purchases

### 5.3 Inventory

### 5.4 Customers and Payments

### 5.5 Suppliers and Payments

### 5.6 Expenses

### 5.7 Reporting

## 6. Requirement Traceability

| Use Case | Related Business Requirements | Related Functional Requirements |
|---|---|---|
| UC-001 — Login | BR-053, BR-056 | FR-001, FR-002 |
| UC-002 — Create Product | BR-001, BR-002, BR-003, BR-004, BR-006, BR-007, BR-081, BR-082 | FR-005, FR-007, FR-008, FR-009 |
| UC-003 — Manage Product Categories | BR-002, BR-081, BR-082 | FR-007 |
| UC-004 — Manage Units | BR-003, BR-081, BR-082 | FR-008 |
| UC-005 — Update Product | BR-001, BR-004, BR-005, BR-006, BR-081, BR-082 | FR-005, FR-009, FR-010 |
| UC-006 — Create Supplier | BR-040, BR-041, BR-042 | FR-018, FR-019 |
| UC-007 — Create Customer | BR-035, BR-036, BR-037, BR-038, BR-039 | FR-013, FR-014 |
| UC-008 — Create Purchase | BR-008, BR-009, BR-010, BR-011, BR-012, BR-013 | FR-023, FR-024, FR-025, FR-026, FR-027 |
| UC-009 — Complete Purchase | BR-008, BR-013, BR-014, BR-026, BR-027, BR-028, BR-044 | FR-028, FR-029 |
| UC-010 — Create Purchase Return | BR-015, BR-016 | FR-030, FR-031, FR-032 |
| UC-011 — Create Sale | BR-016, BR-017, BR-018, BR-019, BR-020, BR-022 | FR-033, FR-034, FR-035, FR-036, FR-037, FR-038 |
| UC-012 — Complete Sale | BR-016, BR-020, BR-022, BR-026, BR-028, BR-039 | FR-039, FR-040 |
| UC-013 — Create Sale Return | BR-025, BR-026 | FR-041, FR-042, FR-043 |
| UC-014 — Record Customer Payment | BR-039, BR-049, BR-051 | FR-044, FR-045, FR-046 |
| UC-015 — Record Supplier Payment | BR-044, BR-049, BR-051 | FR-047, FR-048 |
| UC-016 — Create Inventory Adjustment | BR-031, BR-032, BR-081, BR-082 | FR-049, FR-050, FR-051 |
| UC-017 — Record Expense | BR-045, BR-046, BR-047, BR-048 | FR-057, FR-058, FR-059, FR-060, FR-061, FR-062 |
| UC-018 — Generate Sales Report | BR-058, BR-059, BR-060, BR-061, BR-062, BR-063 | FR-067, FR-068, FR-069, FR-070 |
| UC-019 — Generate Inventory Report | BR-033, BR-034, BR-064, BR-065 | FR-071, FR-072, FR-073 |
| UC-020 — Manage Users | BR-053, BR-054, BR-055, BR-056, BR-057 | FR-063, FR-064, FR-065, FR-066 |

## 7. Open Decisions

- 
- 
- 

## 8. Definition of Done

A use case is considered complete when:

- The primary actor is defined.
- Preconditions are defined.
- The main flow is documented.
- Alternate flows are documented where applicable.
- Postconditions are defined.
- Related requirements are identified.
- Relevant business rules are identified.