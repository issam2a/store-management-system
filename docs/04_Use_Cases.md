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
| UC-002 | Create Product | Owner |
| UC-003 | Update Product | Owner |
| UC-004 | Create Supplier | Owner |
| UC-005 | Create Customer | Owner / Cashier |
| UC-006 | Create Purchase | Owner / Cashier |
| UC-007 | Complete Purchase | Owner / Cashier |
| UC-008 | Create Purchase Return | Owner |
| UC-009 | Create Sale | Owner / Cashier |
| UC-010 | Complete Sale | Owner / Cashier |
| UC-011 | Create Sale Return | Owner |
| UC-012 | Record Customer Payment | Owner / Cashier |
| UC-013 | Record Supplier Payment | Owner / Cashier |
| UC-014 | Create Inventory Adjustment | Owner |
| UC-015 | Record Expense | Owner |
| UC-016 | Generate Sales Report | Owner |
| UC-017 | Generate Inventory Report | Owner |
| UC-018 | Manage Users | Administrator |
| UC-019 | Cancel Transaction | Owner / Authorized User |

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

## UC-006 — Create Supplier

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

## UC-007 — Create Customer

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
| UC-001 | | |
| UC-002 | | |
| UC-003 | | |
| UC-004 | | |
| UC-005 | | |
| UC-006 | | |
| UC-007 | | |
| UC-008 | | |
| UC-009 | | |
| UC-010 | | |
| UC-011 | | |
| UC-012 | | |
| UC-013 | | |
| UC-014 | | |
| UC-015 | | |
| UC-016 | | |
| UC-017 | | |
| UC-018 | | |

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