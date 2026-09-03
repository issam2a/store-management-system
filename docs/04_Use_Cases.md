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
| UC-003 | Manage Product Categories | Owner |
| UC-004 | Manage Units | Owner |
| UC-005 | Update Product | Owner |
| UC-006 | Create Supplier | Owner |
| UC-007 | Create Customer | Owner / Cashier |
| UC-008 | Create Purchase | Owner / Cashier |
| UC-009 | Complete Purchase | Owner / Cashier |
| UC-010 | Create Sale | Owner / Cashier |
| UC-011 | Complete Sale | Owner / Cashier |
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

Allow an authorized user to update the information of an existing product while preserving the accuracy of historical transactions.

### Primary Actor

Owner / Authorized User

### Preconditions

* The user is authenticated.
* The user has permission to update products.
* The product exists in the system.
* The required category and unit are active and available.

### Main Flow

1. The user opens the Product Management module.
2. The user searches for and selects an existing product.
3. The system displays the product's current information.
4. The user selects "Edit Product".
5. The user updates the required product information.
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
10. The system records the update date and time.
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
4. The user provides the required information and resubmits.

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
4. The system preserves the prices and costs stored in completed historical transactions.

#### A6 — Inactive Category or Unit

1. The user attempts to assign an inactive category or unit to the product.
2. The system prevents the selection.
3. The user selects an active category or unit.

### Postconditions

* The product information is updated successfully.
* The product's current/default purchase cost and selling price reflect the latest values.
* The minimum stock level reflects the latest value.
* Historical transaction prices and costs remain unchanged.
* The product update event is recorded for audit purposes.

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

---

## UC-006 — Create Supplier

### Goal

Allow an authorized user to register a supplier in the system so that supplier information, purchases, payments, and outstanding balances can be tracked.

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

1. The user enters information that does not satisfy the defined validation rules.
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

## UC-007 — Create Customer

### Goal

Allow an authorized user to register a customer whose credit transactions, account balance, or payment history needs to be tracked.

### Primary Actor

Owner / Cashier

### Preconditions

* The user is authenticated.
* The user has permission to create customer records.
* The customer requires account tracking or participates in a credit transaction.

### Main Flow

1. The user opens the Customer Management module.
2. The user selects "Create Customer".
3. The system displays the customer creation form.
4. The user enters the customer's information.
5. The user submits the form.
6. The system validates the entered information.
7. The system creates the customer record.
8. The system assigns a unique customer identifier.
9. The system records the customer creation date and time.
10. The system records the user who created the customer.
11. The system displays a confirmation message.

### Alternate Flows

#### A1 — Cash Customer

1. The user creates a cash sale for a walk-in customer.
2. The system does not require a customer record.
3. The sale is recorded without an associated customer account.

#### A2 — Missing Required Information

1. The user submits the form with required information missing.
2. The system rejects the creation request.
3. The system identifies the missing information.
4. The user provides the required information and resubmits.

#### A3 — Duplicate Customer

1. The user enters customer information that conflicts with an existing customer according to the system's uniqueness rules.
2. The system rejects the creation request.
3. The system informs the user that the customer may already exist.
4. The user reviews the existing customer or corrects the information.

#### A4 — Invalid Customer Information

1. The user enters information that does not satisfy the defined validation rules.
2. The system rejects the creation request.
3. The system displays the applicable validation message.
4. The user corrects the information and resubmits.

### Postconditions

* A new customer record exists in the system.
* The customer has a unique identifier.
* The customer is available for credit transactions and account tracking.
* Customer purchases and payments can be associated with the customer account.
* The customer creation event is recorded for audit purposes.

### Related Requirements

* BR-035 — Customer Registration
* BR-036 — Customer Information
* BR-037 — Customer Purchase History
* BR-038 — Customer Payment History
* BR-039 — Customer Debt
* FR-013 — Create Customer


---

## UC-008 — Create Purchase

### Goal

Allow an authorized user to create a purchase transaction containing the products, quantities, and actual purchase costs received from a supplier.

### Primary Actor

Owner / Cashier

### Preconditions

* The user is authenticated.
* The user has permission to create purchase transactions.
* The supplier exists in the system.
* The products included in the purchase exist in the system.
* The products have active units of measurement.

### Main Flow

1. The user opens the Purchase Management module.
2. The user selects "Create Purchase".
3. The system displays a new purchase form.
4. The user selects the supplier.
5. The user adds one or more products to the purchase.
6. For each product, the system displays the product's current/default purchase cost.
7. The user enters the purchased quantity.
8. The user may adjust the unit cost to reflect the actual cost charged by the supplier.
9. The system calculates the line total for each purchase item.
10. The system calculates the total purchase amount.
11. If the purchase is a credit purchase, the system records the purchase as payable to the selected supplier.
12. The user saves the purchase.
13. The system validates the purchase information.
14. The system creates the purchase transaction in Draft status.
15. The system assigns a unique purchase reference.
16. The system records the purchase creation date and time.
17. The system records the user who created the purchase.
18. The system displays the created purchase.

### Alternate Flows

#### A1 — Missing Supplier

1. The user attempts to save the purchase without selecting a supplier.
2. The system rejects the request.
3. The system requires the user to select a supplier.

#### A2 — No Purchase Items

1. The user attempts to save the purchase without adding any products.
2. The system rejects the request.
3. The system requires at least one purchase item.

#### A3 — Invalid Quantity

1. The user enters an invalid quantity.
2. The system rejects the value.
3. The system displays the applicable validation message.
4. The user corrects the quantity.

#### A4 — Invalid Unit Cost

1. The user enters an invalid unit cost.
2. The system rejects the value.
3. The system displays the applicable validation message.
4. The user corrects the unit cost.

#### A5 — Product Not Found

1. The user searches for a product that does not exist.
2. The system does not allow the product to be added.
3. The user selects an existing product or creates the product before continuing.

#### A6 — Actual Cost Differs from Default Cost

1. The supplier charges a unit cost different from the product's current/default purchase cost.
2. The user enters the actual unit cost for the purchase.
3. The system stores the actual unit cost in the purchase item.
4. The product's current/default purchase cost remains unchanged unless the user separately updates it through Product Management.

### Postconditions

* A purchase transaction exists in Draft status.
* The purchase has a unique reference.
* The selected supplier is associated with the purchase.
* One or more purchase items are associated with the purchase.
* Each purchase item stores its actual unit cost and quantity.
* The purchase total is calculated.
* The purchase creation event is recorded.
* Inventory is not updated until the purchase is completed through UC-009.

### Related Requirements

* BR-008 — Purchase Transactions
* BR-009 — Multiple Products per Purchase
* BR-010 — Purchase Quantities
* BR-011 — Purchase Cost
* BR-012 — Purchase Total
* BR-013 — Credit Purchases
* FR-023 — Create Purchase
* FR-024 — Purchase Items
* FR-025 — Purchase Total
* FR-026 — Purchase Payment
* FR-027 — Credit Purchase

---

## UC-009 — Complete Purchase

### Goal

Allow an authorized user to complete a draft purchase transaction so that the purchase is finalized, inventory is updated, and the transaction becomes part of the system's historical records.

### Primary Actor

Owner / Cashier

### Preconditions

* The user is authenticated.
* The user has permission to complete purchase transactions.
* The purchase exists in the system.
* The purchase is in **Draft** status.
* The purchase contains at least one purchase item.
* Each purchase item has a valid product, quantity, and actual unit cost.
* The selected supplier exists and is active.
* The products included in the purchase exist and are active.
* The purchase has passed all required validation checks.

### Main Flow

1. The user opens the Purchase Management module.

2. The user selects a purchase in **Draft** status.

3. The system displays the purchase details.

4. The user reviews the supplier, purchase items, quantities, unit costs, payment type, and calculated total.

5. The user selects **Complete Purchase**.

6. The system validates that the purchase can be completed.

7. The system calculates and confirms the final purchase total.

8. The system verifies that all required purchase information is valid.

9. The system increases the inventory quantity of each purchased product according to the purchase items.

10. If the purchase is **Cash**, the system records the purchase as paid and records the immediate payment associated with the purchase.

11. If the purchase is **Credit**, the system creates the corresponding supplier payable and increases the supplier's outstanding balance by the unpaid purchase amount.

12. The system changes the purchase status from **Draft** to **Completed**.

13. The system records the purchase completion date and time.

14. The system records the user who completed the purchase.

15. The system preserves the actual unit cost stored for each purchase item.

16. The system records the completion event for audit purposes.

17. The system displays a confirmation that the purchase has been completed.


### Alternate Flows

#### A1 — Purchase Already Completed

1. The user attempts to complete a purchase that is already completed.
2. The system rejects the operation.
3. The system informs the user that the purchase has already been completed.

#### A2 — Purchase Cancelled

1. The user attempts to complete a cancelled purchase.
2. The system rejects the operation.
3. The system informs the user that a cancelled purchase cannot be completed.

#### A3 — Invalid Purchase Data

1. The system detects missing or invalid purchase information.
2. The system prevents completion.
3. The system identifies the validation problem.
4. The user corrects the purchase while it is still in Draft status.
5. The user attempts to complete the purchase again.

#### A4 — Product No Longer Available

1. The system detects that a product included in the purchase is no longer active or available for transactions.
2. The system prevents completion.
3. The system identifies the affected product.
4. The user corrects the purchase or updates the product configuration.
5. The user attempts to complete the purchase again.

#### A5 — Concurrent Completion Attempt

1. Two requests attempt to complete the same draft purchase.
2. The system allows only one request to complete the purchase.
3. The other request is rejected because the purchase is no longer in Draft status.
4. Inventory is updated only once.

### Postconditions

* The purchase status is **Completed**.
* The purchase can no longer be edited through the normal purchase workflow.
* Inventory quantities reflect the completed purchase.
* The actual unit cost for each purchase item is preserved.
* The final purchase total is preserved.
* The purchase completion date and time are recorded.
* The user who completed the purchase is recorded.
* Any applicable supplier payable/outstanding balance is updated.
* The completed purchase is available for historical records and reporting.
* The completion event is available for audit purposes.

### Related Requirements

* BR-008 — Supplier Purchases
* BR-013 — Credit Purchases
* BR-014 — Supplier Balance
* BR-026 — Inventory Tracking
* BR-027 — Purchase Inventory Movement
* BR-028 — Sales Inventory Movement
* BR-044 — Supplier Debt
* FR-028 — Purchase Completion
* FR-029 — Purchase Inventory Update

---



## UC-010 — Create Sale

### Goal

Allow an authorized user to create a sale transaction containing the products, quantities, and selling prices to be charged to a customer.

### Primary Actor

Owner / Cashier

### Preconditions

* The user is authenticated.
* The user has permission to create sales.
* The products included in the sale exist in the system.
* The products have active units of measurement.
* For a credit sale, the customer exists in the system and is eligible for account tracking.

### Main Flow

1. The user opens the Sales Management module.
2. The user selects **Create Sale**.
3. The system displays a new sale form.
4. The user selects the applicable customer or chooses to record the sale without a customer.
5. The user adds one or more products to the sale.
6. For each selected product, the system displays the product's current/default selling price.
7. The user enters the quantity sold.
8. The system calculates the line total using the quantity and unit selling price.
9. The system calculates the total sale amount.
10. The user selects the applicable payment method or sale terms.
11. If the sale is a credit sale, the system requires an associated customer account.
12. The user saves the sale.
13. The system validates the sale information.
14. The system creates the sale in **Draft** status.
15. The system assigns a unique sale reference.
16. The system records the sale creation date and time.
17. The system records the user who created the sale.
18. The system displays the created sale.

### Alternate Flows

#### A1 — Cash Sale Without Customer

1. The user creates a sale for a walk-in customer.
2. The user does not select a customer.
3. The system allows the sale to continue.
4. The sale is recorded without an associated customer account.

#### A2 — Credit Sale Without Customer

1. The user selects credit sale or another account-based payment term.
2. No customer is associated with the sale.
3. The system prevents the sale from being saved.
4. The system requires a customer account.
5. The user selects an existing customer or creates a customer record.
6. The user continues with the sale.

#### A3 — Missing Sale Items

1. The user attempts to save the sale without any products.
2. The system rejects the operation.
3. The system requires at least one sale item.
4. The user adds one or more products.

#### A4 — Invalid Quantity

1. The user enters a zero, negative, or otherwise invalid quantity.
2. The system rejects the entered quantity.
3. The system displays the validation error.
4. The user enters a valid quantity.

#### A5 — Invalid Selling Price

1. The sale item contains an invalid selling price.
2. The system rejects the sale.
3. The system displays the validation error.
4. The user corrects the price.

#### A6 — Product Not Found or Inactive

1. The user searches for a product that does not exist or is inactive.
2. The system does not allow the product to be added to the sale.
3. The user selects an available product or corrects the product configuration.

#### A7 — Selling Price Changed Before Completion

1. A product's current/default selling price is changed after the draft sale is created.
2. The system preserves the selling price stored in the existing sale item.
3. The draft sale is completed using the price stored for that sale item unless the user explicitly updates the draft before completion.
4. A new sale uses the product's latest current/default selling price.

### Postconditions

* The sale exists in **Draft** status.
* A unique sale reference has been assigned.
* The sale contains one or more sale items.
* Each sale item stores the quantity and actual unit selling price used for the sale.
* The total sale amount has been calculated.
* The applicable customer association is stored when required.
* The sale creation date and time are recorded.
* The user who created the sale is recorded.
* **Inventory is not updated until the sale is completed through UC-011.**
* The draft sale remains editable through the normal workflow.

### Related Requirements

* BR-016 — Sale Transactions
* BR-017 — Multiple Products per Sale
* BR-018 — Sale Quantities
* BR-019 — Selling Price
* BR-020 — Discounts
* BR-022 — Credit Sales
* BR-039 — Customer Debt
* BR-081 — Data Integrity
* BR-082 — Auditability
* FR-033 — Create Sale
* FR-034 — Sale Items
* FR-035 — Sale Total
* FR-036 — Apply Discount
* FR-037 — Cash Sale
* FR-038 — Credit Sale


---
## UC-011 — Complete Sale

### Goal

Allow an authorized user to complete a draft sale so that the sale is finalized, inventory is updated, applicable financial balances are recorded, and the transaction becomes part of the system's historical records.

### Primary Actor

Owner / Cashier

### Preconditions

* The user is authenticated.
* The user has permission to complete sales.
* The sale exists in the system.
* The sale is in **Draft** status.
* The sale contains at least one sale item.
* Each sale item has a valid product, quantity, and unit selling price.
* The products included in the sale exist and are active.
* The sale has passed all required validation checks.
* For a credit sale, an associated customer account exists.

### Main Flow

1. The user opens the Sales Management module.

2. The user selects a sale in **Draft** status.

3. The system displays the sale details.

4. The user reviews the customer, sale items, quantities, unit selling prices, payment type, and calculated total.

5. The user selects **Complete Sale**.

6. The system validates that the sale can be completed.

7. The system verifies that sufficient inventory is available for each sale item.

8. The system calculates and confirms the final sale total.

9. The system decreases the inventory quantity of each sold product according to the sale items.

10. If the sale is **Cash**, the system records the sale as paid and records the immediate payment associated with the sale.

11. If the sale is **Credit**, the system verifies that a valid customer is associated with the sale, creates the corresponding customer receivable, and increases the customer's outstanding balance by the unpaid sale amount.

12. The system changes the sale status from **Draft** to **Completed**.

13. The system records the sale completion date and time.

14. The system records the user who completed the sale.

15. The system preserves the actual unit selling price stored for each sale item.

16. The system records the completion event for audit purposes.

17. The system displays a confirmation that the sale has been completed.


### Alternate Flows

#### A1 — Sale Already Completed

1. The user attempts to complete a sale that is already completed.
2. The system rejects the operation.
3. The system informs the user that the sale has already been completed.

#### A2 — Sale Cancelled

1. The user attempts to complete a cancelled sale.
2. The system rejects the operation.
3. The system informs the user that a cancelled sale cannot be completed.

#### A3 — Invalid Sale Data

1. The system detects missing or invalid sale information.
2. The system prevents completion.
3. The system identifies the invalid information.
4. The user corrects the sale while it remains in Draft status.
5. The user attempts to complete the sale again.

#### A4 — Insufficient Inventory

1. The system determines that the available inventory is less than the quantity required for one or more sale items.
2. The system prevents completion.
3. The system identifies the affected product and available quantity.
4. The user adjusts the sale quantity or resolves the inventory issue.
5. The user attempts to complete the sale again.

#### A5 — Product No Longer Available

1. The system detects that a product in the draft sale has become inactive or unavailable for sale.
2. The system prevents completion.
3. The system identifies the affected product.
4. The user updates the draft sale or product configuration.
5. The user attempts to complete the sale again.

#### A6 — Credit Sale Without Customer

1. The sale is configured as a credit sale.
2. No customer account is associated with the sale.
3. The system prevents completion.
4. The system requires an eligible customer account.
5. The user associates the sale with a customer.
6. The user attempts to complete the sale again.

#### A7 — Concurrent Completion Attempt

1. Two requests attempt to complete the same draft sale.
2. The system allows only one request to complete the sale.
3. The other request is rejected because the sale is no longer in Draft status.
4. Inventory is deducted only once.

### Postconditions

* The sale status is **Completed**.
* The sale can no longer be edited through the normal workflow.
* Inventory quantities reflect the completed sale.
* The actual unit selling prices used for the sale are preserved.
* The final sale total is preserved.
* Any applicable immediate payment is recorded.
* For credit sales, the customer's outstanding balance is updated.
* The sale completion date and time are recorded.
* The user who completed the sale is recorded.
* The completed sale is available for historical reporting and audit purposes.

### Related Requirements

* BR-016 — Sale Transactions
* BR-018 — Sale Quantities
* BR-019 — Selling Price
* BR-020 — Sale Total
* BR-022 — Credit Sales
* BR-026 — Inventory Tracking
* BR-028 — Sales Inventory Movement
* BR-039 — Customer Debt
* BR-081 — Data Integrity
* BR-082 — Auditability
* FR-039 — Complete Sale
* FR-040 — Update Inventory on Sale Completion

---



## UC-012 — Record Customer Payment

### Goal

Allow an authorized user to record a payment received from a customer and update the customer's outstanding balance accordingly.

### Primary Actor

Owner / Cashier

### Preconditions

* The user is authenticated.
* The user has permission to record customer payments.
* The customer exists in the system.
* The customer has an outstanding balance greater than zero.
* The payment amount is greater than zero.
* The selected payment method is valid.

### Main Flow

1. The user opens the Customer Management or Payments module.
2. The user selects **Record Customer Payment**.
3. The system displays the customer payment form.
4. The user selects the customer.
5. The system displays the customer's current outstanding balance.
6. The user enters the payment amount.
7. The user selects the payment method.
8. The user may enter a payment reference or note when applicable.
9. The user submits the payment.
10. The system validates the payment information.
11. The system verifies that the payment amount does not exceed the customer's outstanding balance, unless overpayments are explicitly supported by the business rules.
12. The system records the customer payment.
13. The system assigns a unique payment reference.
14. The system records the payment date and time.
15. The system records the user who recorded the payment.
16. The system reduces the customer's outstanding balance by the payment amount.
17. The system displays the recorded payment and updated customer balance.

### Alternate Flows

#### A1 — Customer Not Found

1. The user searches for a customer who does not exist.
2. The system informs the user that the customer was not found.
3. The user selects an existing customer or creates a customer record when appropriate.

#### A2 — No Outstanding Balance

1. The user selects a customer with no outstanding balance.
2. The system informs the user that the customer has no outstanding debt.
3. The system prevents the payment from being recorded.

#### A3 — Invalid Payment Amount

1. The user enters a zero, negative, or otherwise invalid amount.
2. The system rejects the payment.
3. The system displays the validation error.
4. The user enters a valid amount.

#### A4 — Payment Exceeds Outstanding Balance

1. The user enters an amount greater than the customer's outstanding balance.
2. The system prevents the payment from being recorded.
3. The system displays the customer's outstanding balance.
4. The user enters a valid payment amount.

#### A5 — Missing Payment Method

1. The user attempts to submit the payment without selecting a payment method.
2. The system rejects the payment.
3. The system requires a valid payment method.
4. The user selects a payment method and resubmits.

#### A6 — Payment Recording Failure

1. The system encounters an error while recording the payment or updating the customer balance.
2. The system does not partially apply the payment.
3. The system informs the user that the payment was not recorded.
4. The user may retry the operation.

### Postconditions

* A customer payment record exists.
* The payment has a unique reference.
* The payment amount and payment method are preserved.
* The payment date and time are recorded.
* The user who recorded the payment is recorded.
* The customer's outstanding balance is reduced by the payment amount.
* The original credit sale remains unchanged.
* The payment is available in the customer's payment history.
* The payment is available for financial reporting and audit purposes.

### Related Requirements

* BR-036 — Customer Payment History
* BR-039 — Customer Debt
* BR-049 — Payment Recording
* BR-051 — Financial Transaction History
* BR-081 — Data Integrity
* BR-082 — Auditability
* FR-044 — Record Customer Payment
* FR-045 — Payment Method
* FR-046 — Partial Payment
* FR-047 — Payment History

---

## UC-013 — Record Supplier Payment

### Goal

Allow an authorized user to record a payment made to a supplier and update the supplier's outstanding balance accordingly.

### Primary Actor

Owner / Cashier

### Preconditions

* The user is authenticated.
* The user has permission to record supplier payments.
* The supplier exists in the system.
* The supplier has an outstanding balance greater than zero.
* The payment amount is greater than zero.
* The selected payment method is valid.

### Main Flow

1. The user opens the Supplier Management or Payments module.
2. The user selects **Record Supplier Payment**.
3. The system displays the supplier payment form.
4. The user selects the supplier.
5. The system displays the supplier's current outstanding balance.
6. The user enters the payment amount.
7. The user selects the payment method.
8. The user may enter a payment reference or note when applicable.
9. The user submits the payment.
10. The system validates the payment information.
11. The system verifies that the payment amount does not exceed the supplier's outstanding balance, unless overpayments are explicitly supported by the business rules.
12. The system records the supplier payment.
13. The system assigns a unique payment reference.
14. The system records the payment date and time.
15. The system records the user who recorded the payment.
16. The system reduces the supplier's outstanding balance by the payment amount.
17. The system displays the recorded payment and updated supplier balance.

### Alternate Flows

#### A1 — Supplier Not Found

1. The user searches for a supplier who does not exist.
2. The system informs the user that the supplier was not found.
3. The user selects an existing supplier or creates a supplier record when appropriate.

#### A2 — No Outstanding Balance

1. The user selects a supplier with no outstanding balance.
2. The system informs the user that the supplier has no outstanding payable balance.
3. The system prevents the payment from being recorded.

#### A3 — Invalid Payment Amount

1. The user enters a zero, negative, or otherwise invalid amount.
2. The system rejects the payment.
3. The system displays the validation error.
4. The user enters a valid amount.

#### A4 — Payment Exceeds Outstanding Balance

1. The user enters an amount greater than the supplier's outstanding balance.
2. The system prevents the payment from being recorded.
3. The system displays the supplier's outstanding balance.
4. The user enters a valid payment amount.

#### A5 — Missing Payment Method

1. The user attempts to submit the payment without selecting a payment method.
2. The system rejects the payment.
3. The system requires a valid payment method.
4. The user selects a payment method and resubmits.

#### A6 — Payment Recording Failure

1. The system encounters an error while recording the payment or updating the supplier balance.
2. The system does not partially apply the payment.
3. The system informs the user that the payment was not recorded.
4. The user may retry the operation.

### Postconditions

* A supplier payment record exists.
* The payment has a unique reference.
* The payment amount and payment method are preserved.
* The payment date and time are recorded.
* The user who recorded the payment is recorded.
* The supplier's outstanding balance is reduced by the payment amount.
* The original purchase remains unchanged.
* The payment is available in the supplier's payment history.
* The payment is available for financial reporting and audit purposes.

### Related Requirements

* BR-042 — Supplier Management
* BR-044 — Supplier Payables
* BR-049 — Payment Recording
* BR-051 — Financial Transaction History
* BR-081 — Data Integrity
* BR-082 — Auditability
* FR-047 — Record Supplier Payment
* FR-048 — Update Supplier Balance

---

## UC-014 — Create Inventory Adjustment

### Goal

Allow an authorized user to create an inventory adjustment to correct the recorded stock quantity when the actual physical inventory differs from the quantity recorded in the system.

### Primary Actor

Owner

### Preconditions

* The user is authenticated.
* The user has permission to create inventory adjustments.
* The product exists in the system.
* The product has an active unit of measurement.
* The user has identified a valid reason for the inventory adjustment.
* The adjustment quantity is valid.

### Main Flow

1. The user opens the Inventory Management module.
2. The user selects **Create Inventory Adjustment**.
3. The system displays the inventory adjustment form.
4. The user selects the product.
5. The system displays the product's current recorded inventory quantity.
6. The user selects the adjustment type:

   * **Increase**
   * **Decrease**
7. The user enters the adjustment quantity.
8. The user enters the reason for the adjustment.
9. The system calculates the resulting inventory quantity.
10. The user reviews the adjustment details.
11. The user submits the adjustment.
12. The system validates the adjustment information.
13. The system records the inventory adjustment.
14. The system updates the product's inventory quantity.
15. The system records the adjustment date and time.
16. The system records the user who created the adjustment.
17. The system displays a confirmation message with the updated inventory quantity.

### Alternate Flows

#### A1 — Product Not Found

1. The user searches for a product that does not exist.
2. The system informs the user that the product was not found.
3. The user selects an existing product or creates the product first.

#### A2 — Invalid Adjustment Quantity

1. The user enters a zero, negative, or otherwise invalid adjustment quantity.
2. The system rejects the adjustment.
3. The system displays the validation error.
4. The user enters a valid quantity.

#### A3 — Insufficient Stock for Decrease

1. The user selects **Decrease**.
2. The requested adjustment would result in a negative inventory quantity.
3. The system prevents the adjustment.
4. The system displays the available inventory quantity.
5. The user enters a valid adjustment quantity.

#### A4 — Missing Adjustment Reason

1. The user attempts to submit the adjustment without providing a reason.
2. The system rejects the adjustment.
3. The system requires an adjustment reason.
4. The user provides the reason and resubmits.

#### A5 — Concurrent Inventory Change

1. Another transaction changes the product's inventory before the adjustment is completed.
2. The system uses the current inventory quantity when applying the adjustment.
3. The system recalculates the resulting quantity.
4. The adjustment is applied only if the resulting inventory quantity remains valid.

#### A6 — Inventory Adjustment Recording Failure

1. The system encounters an error while recording the adjustment or updating inventory.
2. The system does not partially apply the adjustment.
3. The system informs the user that the adjustment was not recorded.
4. The user may retry the operation.

### Postconditions

* An inventory adjustment record exists.
* The adjustment has a recorded type and quantity.
* The adjustment reason is preserved.
* The product's inventory quantity reflects the adjustment.
* The adjustment date and time are recorded.
* The user who created the adjustment is recorded.
* The adjustment is available for inventory history and reporting.
* Historical purchase and sale transactions remain unchanged.
* The adjustment is available for audit purposes.

### Related Requirements

* BR-031 — Inventory Adjustments
* BR-032 — Inventory Accuracy
* BR-081 — Data Integrity
* BR-082 — Auditability
* FR-049 — Create Inventory Adjustment
* FR-050 — Update Inventory Quantity
* FR-051 — Record Adjustment Reason

---

## UC-015 — Record Expense

### Goal

Allow an authorized user to record a business expense so that operating costs are accurately tracked and included in financial reporting.

### Primary Actor

Owner

### Preconditions

* The user is authenticated.
* The user has permission to record expenses.
* The expense amount is greater than zero.
* The expense category is valid.
* The payment method is valid.

### Main Flow

1. The user opens the Expense Management or Financial Management module.
2. The user selects **Record Expense**.
3. The system displays the expense form.
4. The user selects the expense category.
5. The user enters the expense amount.
6. The user selects the payment method.
7. The user enters the expense date.
8. The user may enter a description or note.
9. The user submits the expense.
10. The system validates the entered information.
11. The system records the expense.
12. The system assigns a unique expense reference.
13. The system records the expense date and time.
14. The system records the user who created the expense.
15. The system records the expense as a financial transaction.
16. The system displays a confirmation message.

### Alternate Flows

#### A1 — Missing Expense Category

1. The user attempts to submit the expense without selecting a category.
2. The system rejects the expense.
3. The system requires an expense category.
4. The user selects a category and resubmits.

#### A2 — Invalid Expense Amount

1. The user enters a zero, negative, or otherwise invalid amount.
2. The system rejects the expense.
3. The system displays the validation error.
4. The user enters a valid amount.

#### A3 — Missing Payment Method

1. The user attempts to submit the expense without selecting a payment method.
2. The system rejects the expense.
3. The system requires a valid payment method.
4. The user selects a payment method and resubmits.

#### A4 — Invalid Expense Date

1. The user enters an invalid expense date.
2. The system rejects the expense.
3. The system displays the validation error.
4. The user enters a valid date.

#### A5 — Missing Description

1. The user submits the expense without a description.
2. If the description is optional, the system continues with the expense.
3. If the description is required for the selected expense category, the system requests the missing information.
4. The user provides the required information and resubmits.

#### A6 — Expense Recording Failure

1. The system encounters an error while recording the expense.
2. The system does not partially record the expense.
3. The system informs the user that the expense was not recorded.
4. The user may retry the operation.

### Postconditions

* An expense record exists.
* The expense has a unique reference.
* The expense category and amount are preserved.
* The payment method is preserved.
* The expense date is recorded.
* The user who recorded the expense is recorded.
* The expense is available for financial reporting.
* The expense is available for audit purposes.
* Inventory quantities are not changed by the expense.

### Related Requirements

* BR-045 — Expense Recording
* BR-046 — Expense Categories
* BR-047 — Expense Information
* BR-048 — Expense Reporting
* BR-081 — Data Integrity
* BR-082 — Auditability
* FR-057 — Record Expense
* FR-058 — Record Expense Amount
* FR-059 — Record Expense Category
* FR-060 — Record Expense Payment Method
* FR-061 — Record Expense Date
* FR-062 — Include Expenses in Financial Reporting


---

## UC-016 — Generate Sales Report

### Goal

Allow an authorized user to generate a sales report that summarizes completed sales and provides the information needed to monitor sales performance and support business decisions.

### Primary Actor

Owner / Authorized User

### Preconditions

* The user is authenticated.
* The user has permission to view sales reports.
* The system contains completed sales or the selected report period is valid.

### Main Flow

1. The user opens the Reports module.
2. The user selects **Sales Report**.
3. The system displays the available report filters.
4. The user selects the required reporting period.
5. The user may apply additional filters such as:

   * Product
   * Product category
   * Payment method
   * Customer
6. The user requests the report.
7. The system retrieves completed sales matching the selected criteria.
8. The system excludes Draft and Cancelled sales from normal sales totals.
9. The system calculates the applicable sales metrics.
10. The system displays the sales report.
11. The system displays the report period and applied filters.
12. The user may review the underlying sales transactions included in the report.

### Sales Report Information

The report shall provide, where applicable:

* Total sales amount
* Number of completed sales
* Total quantity sold
* Average sale value
* Sales by product
* Sales by product category
* Sales by payment method
* Sales by customer for account-tracked customers
* Sales trend over the selected period
* Credit sales amount
* Cash sales amount

### Alternate Flows

#### A1 — No Sales Found

1. The user generates a report for a period with no completed sales.
2. The system displays the report with zero sales values.
3. The system informs the user that no completed sales were found for the selected criteria.

#### A2 — Invalid Date Range

1. The user enters an invalid date range.
2. The system rejects the report request.
3. The system identifies the date validation error.
4. The user provides a valid date range and requests the report again.

#### A3 — Invalid Filter Combination

1. The user selects filters that are invalid or incompatible.
2. The system rejects the report request.
3. The system identifies the invalid filter.
4. The user modifies the filters and requests the report again.

#### A4 — Cancelled Sales

1. The selected reporting period contains cancelled sales.
2. The system excludes cancelled sales from normal sales totals.
3. The cancelled transactions remain available through appropriate historical or audit information.

#### A5 — Report Generation Failure

1. The system encounters an error while generating the report.
2. The system does not display incomplete or misleading report results.
3. The system informs the user that the report could not be generated.
4. The user may retry the report.

### Postconditions

* A sales report is generated based on completed sales.
* The selected reporting period is displayed.
* Applied filters are displayed.
* Sales metrics are calculated from the applicable completed transactions.
* Draft sales are excluded from sales totals.
* Cancelled sales are excluded from normal sales totals.
* The report can be used for sales analysis and business decision-making.
* The underlying historical sales transactions remain unchanged.

### Related Requirements

* BR-058 — Sales Reporting
* BR-059 — Sales Metrics
* BR-060 — Sales Filtering
* BR-061 — Sales Analysis
* BR-062 — Sales History
* BR-063 — Sales Reporting Accuracy
* BR-081 — Data Integrity
* BR-082 — Auditability
* FR-067 — Generate Sales Report
* FR-068 — Filter Sales Report
* FR-069 — Calculate Sales Metrics
* FR-070 — Display Sales Report

---
## UC-017 — Generate Inventory Report

### Goal

Allow an authorized user to generate an inventory report that provides an accurate view of current stock levels, identifies products requiring attention, and supports inventory management decisions.

### Primary Actor

Owner / Authorized User

### Preconditions

* The user is authenticated.
* The user has permission to view inventory reports.
* Products exist in the system.

### Main Flow

1. The user opens the Reports module.
2. The user selects **Inventory Report**.
3. The system displays the available report filters.
4. The user may filter the report by:

   * Product
   * Product category
   * Stock status
5. The user requests the report.
6. The system retrieves the current inventory information.
7. The system calculates the current stock quantity for each applicable product.
8. The system compares each product's current stock quantity with its minimum stock level.
9. The system identifies products with low or insufficient stock.
10. The system displays the inventory report.
11. The system displays the report filters and relevant inventory information.
12. The user may review the inventory position and identify products requiring replenishment or investigation.

### Inventory Report Information

The report shall provide, where applicable:

* Product name
* Product category
* Unit of measurement
* Current stock quantity
* Minimum stock level
* Stock status
* Products below minimum stock level
* Products with zero stock
* Products with available stock

The report may also provide inventory movement information for a selected period, including:

* Quantity purchased
* Quantity sold
* Inventory increases from adjustments
* Inventory decreases from adjustments
* Net inventory movement

### Alternate Flows

#### A1 — No Products Found

1. The user generates the report with filters that match no products.
2. The system displays an empty report.
3. The system informs the user that no products match the selected criteria.

#### A2 — No Low-Stock Products

1. The user generates a report filtered for low-stock products.
2. No products meet the low-stock condition.
3. The system displays an empty low-stock result.
4. The system indicates that no products currently require replenishment based on their minimum stock levels.

#### A3 — Invalid Filter

1. The user selects an invalid or incompatible filter.
2. The system rejects the report request.
3. The system identifies the invalid filter.
4. The user corrects the filter and requests the report again.

#### A4 — Report Generation Failure

1. The system encounters an error while generating the report.
2. The system does not display incomplete or misleading inventory information.
3. The system informs the user that the report could not be generated.
4. The user may retry the report.

### Postconditions

* An inventory report is generated using the current inventory information.
* The selected filters are displayed.
* Current stock quantities are displayed for applicable products.
* Products below their minimum stock levels are identified.
* Inventory information reflects completed purchases, completed sales, and recorded inventory adjustments.
* Draft transactions do not affect the reported current stock.
* The report does not modify inventory or historical transactions.
* The report can be used for inventory monitoring and replenishment decisions.

### Related Requirements

* BR-033 — Inventory Reporting
* BR-034 — Inventory Information
* BR-064 — Inventory Status
* BR-065 — Inventory Reporting Accuracy
* BR-081 — Data Integrity
* BR-082 — Auditability
* FR-071 — Generate Inventory Report
* FR-072 — Display Inventory Information
* FR-073 — Identify Low-Stock Products

---

## UC-018 — Manage Users

### Goal

Allow an authorized administrator to create, view, update, activate, and deactivate system user accounts and assign appropriate roles and permissions.

### Primary Actor

Owner / Administrator

### Preconditions

* The user is authenticated.
* The user has permission to manage users.
* The system has the required user roles configured.

### Main Flow

1. The administrator opens the **User Management** module.
2. The system displays the existing user accounts.
3. The administrator selects an action such as:

   * Create User
   * View User
   * Update User
   * Activate User
   * Deactivate User
4. For a new user, the administrator enters the required account information.
5. The administrator assigns an appropriate role to the user.
6. The administrator submits the changes.
7. The system validates the user information and assigned role.
8. The system creates or updates the user account.
9. The system assigns a unique user identifier when creating a new account.
10. The system records the account creation or update date and time.
11. The system records the administrator who performed the operation.
12. The system displays a confirmation message.

### Alternate Flows

#### A1 — Duplicate Username

1. The administrator enters a username that already exists.
2. The system rejects the operation.
3. The system informs the administrator that the username is already in use.
4. The administrator enters a different username.

#### A2 — Invalid User Information

1. The administrator enters missing or invalid required information.
2. The system rejects the operation.
3. The system displays the validation errors.
4. The administrator corrects the information and resubmits.

#### A3 — Invalid Role

1. The administrator attempts to assign an invalid or unavailable role.
2. The system rejects the operation.
3. The system requires a valid configured role.
4. The administrator selects an appropriate role.

#### A4 — Deactivate User

1. The administrator selects an active user account.
2. The administrator selects **Deactivate**.
3. The system requests confirmation.
4. The administrator confirms the operation.
5. The system marks the user account as inactive.
6. The inactive user can no longer authenticate to the system.
7. The user's historical transactions and audit records remain unchanged.

#### A5 — Activate User

1. The administrator selects an inactive user account.
2. The administrator selects **Activate**.
3. The system requests confirmation.
4. The administrator confirms the operation.
5. The system marks the user account as active.
6. The user can authenticate according to the assigned role and permissions.

#### A6 — Attempt to Deactivate Current Administrator

1. The administrator attempts to deactivate their own account or the only remaining administrator account.
2. The system prevents the operation if it would leave the system without an active administrator.
3. The system informs the administrator that at least one authorized administrator account must remain active.

#### A7 — User Already Has Historical Transactions

1. The administrator attempts to deactivate a user who has created or completed historical transactions.
2. The system allows the account to be deactivated.
3. The user's historical transactions continue to reference the original user.
4. The system does not delete or modify the historical records.

### Postconditions

* A new user account may be created.
* Existing user information may be updated.
* User roles and permissions are maintained.
* User accounts may be activated or deactivated.
* Deactivated users cannot access the system.
* Historical transactions remain associated with the user who performed them.
* User management actions are recorded for audit purposes.
* At least one active administrator remains available to manage the system.

### Related Requirements

* BR-053 — User Authentication
* BR-054 — User Roles
* BR-055 — User Permissions
* BR-056 — User Account Management
* BR-057 — User Auditability
* BR-081 — Data Integrity
* BR-082 — Auditability
* FR-063 — Create User
* FR-064 — Manage User Information
* FR-065 — Manage User Roles and Permissions
* FR-066 — Activate or Deactivate User

## UC-019 — Cancel Transaction

### Goal

Allow an authorized user to cancel a completed sale or purchase while preserving the original transaction and maintaining accurate inventory, financial records, and audit history.

### Primary Actor

Owner / Authorized User

### Preconditions

* The user is authenticated.
* The user has permission to cancel transactions.
* The transaction exists in the system.
* The transaction has been completed.
* The transaction has not already been cancelled.

### Main Flow

1. The user opens the transaction management module.
2. The user searches for and selects a completed sale or purchase.
3. The system displays the transaction details.
4. The user selects "Cancel Transaction".
5. The system displays a cancellation confirmation.
6. The user provides a cancellation reason.
7. The user confirms the cancellation.
8. The system validates that the transaction can be cancelled.
9. The system changes the transaction status from `Completed` to `Cancelled`.
10. The system records the cancellation date and time.
11. The system records the user who performed the cancellation.
12. The system reverses the inventory movement created by the original transaction:

    * For a cancelled sale, the sold quantity is returned to inventory.
    * For a cancelled purchase, the purchased quantity is removed from inventory.
13. The system reverses the applicable financial effect of the transaction according to its payment or credit status.
14. The system preserves the original transaction details and transaction amounts.
15. The system records the cancellation reason.
16. The system records the cancellation event for audit purposes.
17. The system displays a confirmation message.

### Alternate Flows

#### A1 — Transaction Not Found

1. The user searches for a transaction that does not exist.
2. The system displays an appropriate message.
3. The user searches for another transaction.

#### A2 — Transaction Already Cancelled

1. The user selects a transaction that has already been cancelled.
2. The system prevents cancellation.
3. The system informs the user that the transaction has already been cancelled.

#### A3 — Transaction Is Not Completed

1. The user selects a draft transaction.
2. The system prevents cancellation through this process.
3. The user may edit or complete the draft according to the applicable workflow.

#### A4 — Missing Cancellation Reason

1. The user attempts to confirm the cancellation without providing a reason.
2. The system rejects the cancellation.
3. The system requests a cancellation reason.
4. The user provides the reason and confirms again.

#### A5 — Insufficient Inventory for Purchase Cancellation

1. The user attempts to cancel a completed purchase.
2. The system determines that the required quantity is no longer available in inventory.
3. The system prevents the cancellation from creating an invalid stock quantity.
4. The system informs the user that the transaction requires review before cancellation.

#### A6 — Concurrent Transaction Update

1. Another transaction modifies the affected inventory or financial records while cancellation is being processed.
2. The system detects the conflicting update.
3. The system prevents an inconsistent cancellation.
4. The user is informed that the transaction must be reviewed again.

#### A7 — Cancellation Recording Failure

1. An error occurs while recording the cancellation or applying its related effects.
2. The system rolls back the cancellation operation.
3. The original transaction remains unchanged.
4. The system displays an error message.

### Postconditions

* The original transaction remains stored in the system.
* The transaction status is `Cancelled`.
* The cancellation reason is stored.
* The cancellation date and time are recorded.
* The user who performed the cancellation is recorded.
* The inventory effect of the original transaction is reversed.
* The applicable financial effect is reversed according to the transaction's payment or credit status.
* The original transaction details and historical transaction prices remain unchanged.
* The cancellation is included in the audit history.
* Cancelled transactions are excluded from normal completed-sales and completed-purchases reporting.

### Related Requirements

* BR-008

* BR-013

* BR-014

* BR-026

* BR-027

* BR-028

* BR-039

* BR-044

* BR-081

* BR-082

* FR-028

* FR-029

* FR-039

* FR-040




---

## 5. Use Case Relationships

### 5.1 Product Management

* UC-002 Create Product requires an existing Product Category (UC-003) and Unit (UC-004).
* UC-005 Update Product modifies product information used by purchasing, sales, inventory, and reporting processes.
* Products created through UC-002 are used in purchases, sales, inventory adjustments, and reports.

### 5.2 Purchasing Process

* UC-006 Create Supplier provides supplier records used in purchasing.
* UC-008 Create Purchase creates a draft purchase transaction.
* UC-009 Complete Purchase finalizes the purchase and updates inventory.
* Completed purchases increase inventory quantities.
* Credit purchases create supplier balances that are later reduced through UC-015 Record Supplier Payment.

### 5.3 Sales Process

* UC-007 Create Customer provides customer records for credit sales.
* UC-010 Create Sale creates a draft sale transaction.
* UC-011 Complete Sale finalizes the sale and updates inventory.
* Completed sales decrease inventory quantities.
* Credit sales create customer balances that are later reduced through UC-014 Record Customer Payment.

### 5.4 Inventory Management

* UC-009 Complete Purchase increases inventory.
* UC-011 Complete Sale decreases inventory.
* UC-016 Create Inventory Adjustment manually corrects inventory quantities.
* UC-019 Cancel Transaction may reverse inventory movements when a completed transaction is cancelled.
* UC-019 does not delete historical records.

### 5.5 Financial Management

* UC-014 Record Customer Payment reduces customer outstanding balances created by credit sales.
* UC-015 Record Supplier Payment reduces supplier outstanding balances created by credit purchases.
* UC-017 Record Expense records business operating expenses.
* Financial records contribute to reporting and business analysis.

### 5.6 Reporting

* UC-018 Generate Sales Report uses completed sales transactions.
* UC-019 Generate Inventory Report uses inventory quantities and inventory movement history.
* Reports use information generated by purchasing, sales, inventory, customer, supplier, and financial processes.

### 5.7 User Administration

* UC-020 Manage Users controls system access.
* User roles determine which use cases each user may perform.
* User information is recorded in audit trails throughout the system.

### 5.8 Transaction Cancellation

* UC-021 Cancel Transaction applies only to completed transactions.
* Cancelling a completed purchase reverses the inventory increase and any related financial impact.
* Cancelling a completed sale reverses the inventory decrease and any related financial impact.
* Cancelled transactions remain available for audit and reporting purposes.




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
| UC-019 | | |

## 7. Open Decisions

### OD-001 — Product Barcode Support

The business has not yet decided whether products will be identified only by name and internal product code or whether barcode scanning functionality will be required.

### OD-002 — Customer Credit Limit

The business has not yet decided whether customers should have configurable credit limits that restrict additional credit sales when the limit is exceeded.

### OD-003 — Supplier Credit Limit

The business has not yet decided whether supplier balances should be monitored against configurable credit limits.

### OD-004 — Transaction Cancellation Authorization

The business has not yet decided which user roles may cancel completed transactions and whether additional approval is required for high-value cancellations.

### OD-005 — Expense Categories

The final list of expense categories has not yet been defined and may be refined during detailed design.

### OD-006 — Reporting Export Formats

The business has not yet decided whether reports should support export to PDF, Excel, CSV, or multiple formats.

### OD-007 — Multi-Store Support

The business has not yet decided whether the system will support only a single store location or multiple store locations in the future.


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