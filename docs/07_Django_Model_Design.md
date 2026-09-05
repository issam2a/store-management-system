# 07 — Django Model Design 

## 0. Revision Note

This is a revision of the original `07_Django_Model_Design.md`. It resolves ten open design issues identified during review, before any model code is written. This document — not the original draft — is the implementation blueprint.

**Cross-check against `06_Database_Design.md` (second pass):** the original draft, and an earlier version of this revision, had inconsistently added `discount_amount` fields to `Purchase`, `PurchaseItem`, and `SaleItem`. The approved database design (§11, §12, §14, §40) specifies a **sale-level-only** discount model with no discount field anywhere except `Sale`. Those extra fields have been removed throughout this document, and the missing `Sale` constraints (`discount_amount <= subtotal_amount`, `total_amount = subtotal_amount - discount_amount`) have been added to §21.

No new business behavior has been introduced. Where a business decision is genuinely open (inventory costing method), it remains explicitly open here rather than being silently resolved.

---

## 1. Purpose

This document defines the Django model architecture for the Store Management & Business Analytics System.

The design translates the approved database schema into Django ORM models while preserving:

- Business rules
- Database constraints
- Transaction lifecycle rules
- Audit requirements
- Inventory integrity
- Financial integrity

The models defined here will become the source for Django migrations and PostgreSQL table creation.

---

## 2. Design Principles

The Django models shall:

- Map directly to the approved database design.
- Use Django foreign keys for relationships.
- Use model validation where business rules require it and where the rule can be checked on a single row without locking.
- Use PostgreSQL constraints for invariants that must hold regardless of code path (including manual SQL or a buggy migration).
- Use the service layer for anything involving multiple rows, concurrency, or state transitions.
- Preserve historical transaction accuracy.
- Prevent invalid business states.
- Support future system growth.

---

## 3. Model Overview

```text
Category
Unit
Product

Supplier
Customer

Purchase
PurchaseItem

Sale
SaleItem

CustomerPayment
SupplierPayment

InventoryAdjustment

Expense

TransactionCancellation
```

Authentication shall use:

```text
django.contrib.auth.models.User
```

No custom user table is required for V1.

---

## 4. Audit Field Matrix (Resolved)

Audit fields are assigned per-model rather than added everywhere by default. A field only appears on a model if that model has the corresponding lifecycle stage.

| Model | created_at/by | completed_at/by | cancelled_at/by | recorded_by |
|---|---|---|---|---|
| Category | ✅ (updated_at too) | — | — | — |
| Unit | ✅ (updated_at too) | — | — | — |
| Product | ✅ (updated_at too) | — | — | — |
| Supplier | ✅ (updated_at too) | — | — | — |
| Customer | ✅ (updated_at too) | — | — | — |
| Purchase | ✅ | ✅ | ✅ | — |
| PurchaseItem | — (inherits via Purchase) | — | — | — |
| Sale | ✅ | ✅ | ✅ | — |
| SaleItem | — (inherits via Sale) | — | — | — |
| CustomerPayment | ✅ (created_at only) | — | — | ✅ |
| SupplierPayment | ✅ (created_at only) | — | — | ✅ |
| InventoryAdjustment | ✅ (created_at only) | — | — | — (uses created_by) |
| Expense | ✅ (created_at only) | — | — | — (uses created_by) |
| TransactionCancellation | — | — | ✅ | — |

Rationale: `InventoryAdjustment`, `Expense`, `CustomerPayment`, and `SupplierPayment` are single-step records — they don't have a DRAFT/COMPLETED/CANCELLED lifecycle, so `completed_by`/`cancelled_by` don't apply to them. Only `Purchase` and `Sale` carry the full lifecycle audit trail.

All user references use:

```python
settings.AUTH_USER_MODEL
```

`on_delete` behavior for these fields is `PROTECT` in every case — see §22a for the full decision and rationale.

---

## 5. Category Model

### Fields
```text
id
name
is_active
created_at
updated_at
```

### Relationships
```text
Category
    |
    └── Product (1:N)
```

### Rules
- `name` unique
- cannot delete if referenced (enforced via `on_delete=PROTECT` from Product, see §21)
- inactive categories not selectable in UI/service layer (not a DB-level rule)

---

## 6. Unit Model

### Fields
```text
id
name
symbol
is_active
created_at
updated_at
```

### Rules
- `name` unique
- `symbol` unique
- inactive units not selectable

---

## 7. Product Model

### Fields
```text
id
name
category
unit
current_purchase_cost
current_sell_price
minimum_stock
current_stock
is_active
created_at
updated_at
```

### Relationships
```text
Category → Product   (on_delete=PROTECT)
Unit → Product        (on_delete=PROTECT)
```

### Validation (model `clean()` + DB CheckConstraint)
```text
current_purchase_cost >= 0
current_sell_price >= 0
minimum_stock >= 0
current_stock >= 0   -- DB CheckConstraint (see §9 for concurrency note)
```

### Business Rules
- inactive products cannot be added to any new transaction — sales, purchases, or inventory adjustments alike — enforced in the service layer at the point of adding a line item / adjustment (broadened from the earlier "cannot be sold" wording, which understated the rule)
- historical prices are stored on PurchaseItem/SaleItem, not recalculated from Product
- `current_stock` is live operational stock, mutated only via service methods under row-level locking (see §9)

---

## 8. Supplier Model

### Fields
```text
id
name
phone
contact_information
is_active
created_at
updated_at
```

### Rules
- `name` required
- inactive suppliers cannot be selected (service-layer enforcement)

---

## 9. Customer Model

### Fields
```text
id
name
phone
contact_information
account_status
created_at
updated_at
```

### Rules
- cash sales do not require a customer
- credit sales require a customer (enforced in `Sale.clean()`, see §12)
- **no stored balance field.** Customer balance is always derived, never cached on the model (see §16.1). This closes design issue #8.

---

## 10. Purchase Model

### Fields
```text
id
reference
supplier
payment_type
status
total_amount
created_at
created_by
completed_at
completed_by
cancelled_at
cancelled_by
```

Note: per `06_Database_Design.md` §11 and §40, V1 uses a **sale-level discount model only**. `Purchase` has no `subtotal_amount` or `discount_amount` field — only `total_amount`. An earlier draft of this document incorrectly added discount fields to Purchase; this has been corrected to match the approved database design.

### Enums
```text
Payment Type: CASH, CREDIT
Status: DRAFT, COMPLETED, CANCELLED
```

### Relationships
```text
Supplier → Purchase   (on_delete=PROTECT)
Purchase → PurchaseItem   (on_delete=CASCADE, from PurchaseItem's FK to Purchase)
```

Rationale for `CASCADE` here (as opposed to `PROTECT`): `PurchaseItem` rows have no independent existence — they are the line items *of* a specific `Purchase` and carry no meaning without their parent. This is the inverse situation from §22/§22a, where the FK points *up* to shared master data or a user account that other rows also depend on. Here the FK points *down* to child rows that belong exclusively to one parent. Since completed/cancelled purchases are never physically deleted through normal application functionality anyway (per the DB design's delete strategy), `CASCADE` only ever fires in practice if a `Purchase` is deleted through an unusual/administrative path — and in that case the child items should go with it, not be orphaned or block the delete.

### Totals Policy (resolves design issue #5)
`total_amount` is a **stored snapshot**, not dynamically calculated. It is:
- computed once by `complete_purchase()` from the associated `PurchaseItem` rows at the moment of completion,
- writable only by that service method,
- immutable afterward — never recomputed on read, and never edited directly on the model instance.

This is consistent with `PurchaseItem.unit_cost` being immutable after completion (§11).

### State Machine (resolves design issue #4)
See §17 for the shared state-transition rules that apply to both Purchase and Sale.

---

## 11. PurchaseItem Model

### Fields
```text
id
purchase
product
quantity
unit_cost
line_total
```

Note: no `discount_amount` field — matches `06_Database_Design.md` §12, which defines no discount mechanism on purchases or purchase items in V1.

### Relationships
```text
Product → PurchaseItem   (on_delete=PROTECT)   -- resolves design issue #1
```

### Rules (DB CheckConstraints)
```text
quantity > 0
unit_cost >= 0
line_total >= 0
```

### Historical Rule
```text
unit_cost is immutable after the parent Purchase reaches COMPLETED.
Enforced in the service layer: complete_purchase() is the only path that
finalizes this row; no update path exists afterward.
```

---

## 12. Sale Model

### Fields
```text
id
reference
customer
payment_type
status
subtotal_amount
discount_amount
total_amount
created_at
created_by
completed_at
completed_by
cancelled_at
cancelled_by
```

### Relationships
```text
Customer → Sale   (on_delete=PROTECT)
Sale → SaleItem   (on_delete=CASCADE, from SaleItem's FK to Sale — same rationale as PurchaseItem, §10)
```

### Validation
```text
payment_type = CREDIT  =>  customer required
```
Enforced in `Sale.clean()` — this is a single-row check with no locking requirement, so it belongs in model validation, not the service layer.

### Totals Policy
Same stored-snapshot policy as Purchase (§10) — `total_amount` etc. are written once by `complete_sale()` and are immutable afterward.

### State Machine
See §17.

---

## 13. SaleItem Model

### Fields
```text
id
sale
product
quantity
unit_price
line_total
```

Note: no `discount_amount` field on `SaleItem` — `06_Database_Design.md` §14 states this explicitly: discounts are sale-level only, and `SaleItem.unit_price`/`line_total` must stay independent of the sale-level discount. An earlier draft incorrectly added this field; corrected here.

### Relationships
```text
Product → SaleItem   (on_delete=PROTECT)   -- resolves design issue #1
```

### Rules (DB CheckConstraints)
```text
quantity > 0
unit_price >= 0
line_total >= 0
```

### Historical Rule
```text
unit_price is immutable after the parent Sale reaches COMPLETED, enforced
the same way as PurchaseItem.unit_cost (§11).
```

---

## 14. CustomerPayment Model

### Fields
```text
id
reference
customer
amount
payment_method
payment_date
note
recorded_by
created_at
```

### Relationships
```text
Customer → CustomerPayment   (on_delete=PROTECT)
```

### Rules
```text
amount > 0   -- DB CheckConstraint
```

### Balance Usage (resolves design issue #8)
`CustomerPayment` rows are never aggregated into a stored balance field. Balance is always computed on demand — see §16.1.

---

## 15. SupplierPayment Model

### Fields
```text
id
reference
supplier
amount
payment_method
payment_date
note
recorded_by
created_at
```

### Relationships
```text
Supplier → SupplierPayment   (on_delete=PROTECT)
```

### Rules
```text
amount > 0   -- DB CheckConstraint
```

Same non-cached-balance policy as CustomerPayment — see §16.1.

---

## 16. InventoryAdjustment Model

### Fields
```text
id
reference
product
adjustment_type
quantity
reason
created_at
created_by
```

### Relationships
```text
Product → InventoryAdjustment   (on_delete=PROTECT)
```

### Enum
```text
INCREASE, DECREASE
```

### Rules
```text
reason required
quantity > 0            -- DB CheckConstraint
```

### Stock-Floor Rule (resolves design issue #9)
"Cannot reduce stock below zero" **cannot** be fully guaranteed by a model-level constraint, because it depends on the current value of a different row (`Product.current_stock`) at write time — a classic race-condition-prone check. It is enforced as follows:

1. **Service layer**: `apply_inventory_adjustment()` runs inside `transaction.atomic()`, takes `select_for_update()` on the target `Product` row, checks the resulting stock would not go negative, and only then writes both the `InventoryAdjustment` row and the updated `Product.current_stock`.
2. **Database backstop**: the `CheckConstraint current_stock >= 0` on `Product` (§7) still exists as a last line of defense in case a non-service code path ever touches this table directly.

### 16.1 Balance / Stock Derivation Policy

Both customer/supplier balances and product stock levels follow the same principle: **the authoritative value is either a locked, atomically-maintained field (`Product.current_stock`) or a derived query (`Customer`/`Supplier` balance) — never a field that's opportunistically incremented outside a locked transaction.**

```text
customer_balance(customer) =
    sum(total_amount for completed CREDIT Sales of customer)
  - sum(amount for CustomerPayments of customer)

supplier_balance(supplier) =
    sum(total_amount for completed CREDIT Purchases of supplier)
  - sum(amount for SupplierPayments of supplier)
```

These are implemented as service-layer/query functions (or, later, DB views) — not model fields.

---

## 17. Transaction Lifecycle State Machine (resolves design issue #4)

Applies to both `Purchase.status` and `Sale.status`.

```text
Allowed transitions:
  DRAFT      -> COMPLETED
  COMPLETED  -> CANCELLED

Explicitly disallowed (must be rejected by the service layer):
  DRAFT      -> CANCELLED
  CANCELLED  -> COMPLETED
  CANCELLED  -> DRAFT
  COMPLETED  -> DRAFT
  any status -> itself
```

### Enforcement

- Represented as a single source-of-truth mapping in the service layer, e.g.:
  ```python
  ALLOWED_TRANSITIONS = {
      "DRAFT": {"COMPLETED"},
      "COMPLETED": {"CANCELLED"},
      "CANCELLED": set(),
  }
  ```
- Every transition method (`complete_sale()`, `cancel_sale()`, `complete_purchase()`, `cancel_purchase()`) must:
  1. Run inside `transaction.atomic()`.
  2. Take `select_for_update()` on the `Sale`/`Purchase` row before checking `status`.
  3. Reject the call if the transition isn't in `ALLOWED_TRANSITIONS`.
  4. Only then perform the associated side effects (stock changes, totals snapshot, audit fields).
- This state machine is a service-layer rule, not a DB constraint, because the valid-transition set depends on the row's current value at the time of the write and pairs naturally with the locking already required for stock mutation.

---

## 18. Expense Model

### Fields
```text
id
reference
category
amount
payment_method
expense_date
description
created_at
created_by
```

### Rules
```text
amount > 0   -- DB CheckConstraint
```

---

## 19. TransactionCancellation Model

### Fields
```text
id
sale
purchase
reason
cancelled_at
cancelled_by
```

### Relationships
```text
Sale → TransactionCancellation       (on_delete=PROTECT)
Purchase → TransactionCancellation   (on_delete=PROTECT)
```

Rationale: a cancellation record is itself a historical/audit artifact — it documents why and when a transaction was reversed. Deleting the parent `Sale`/`Purchase` must not be allowed to silently take the cancellation record with it (as `CASCADE` would), nor should the cancellation ever end up pointing at nothing (as `SET_NULL` would allow, which would also break the CheckConstraint further below in this section since `sale`/`purchase` would both become null). This is the same master-data/historical-integrity principle already applied in §22 — extended here from "master data" to "the transaction being cancelled," since a `Sale`/`Purchase` that already has an approved delete-blocking rule (they're never physically deleted per business rule anyway) should not have a weaker rule via a second path.

### Validation — Resolved (design issue #3)

Previously stated only as a business rule ("exactly one of sale/purchase, never both, one cancellation per transaction"). Now enforced at the database level:

```python
class Meta:
    constraints = [
        models.CheckConstraint(
            check=(
                Q(sale__isnull=False, purchase__isnull=True) |
                Q(sale__isnull=True, purchase__isnull=False)
            ),
            name="exactly_one_of_sale_or_purchase",
        ),
        models.UniqueConstraint(
            fields=["sale"],
            condition=Q(sale__isnull=False),
            name="unique_cancellation_per_sale",
        ),
        models.UniqueConstraint(
            fields=["purchase"],
            condition=Q(purchase__isnull=False),
            name="unique_cancellation_per_purchase",
        ),
    ]
```

This guarantees both "exactly one of the two" and "at most one cancellation row per transaction" at the DB layer, not just in application code.

---

## 20. Django Choices

The following fields shall use Django Choices (`TextChoices`/`IntegerChoices`):

```text
Purchase.status
Sale.status
Purchase.payment_type
Sale.payment_type
InventoryAdjustment.adjustment_type
```

Note: `Customer.account_status` is **not** included here. `06_Database_Design.md` §10 defines `account_status` as `VARCHAR, Required` but does not enumerate a fixed set of values or restrict it to a closed choice list the way it does for `Purchase.status`/`Sale.status` (§21) or `Purchase.payment_type`/`Sale.payment_type` (§24). Until the approved documents define the actual set of account-status values, this field is implemented as an unrestricted `CharField`, not a `Choices` enum — adding a choice list here would be inventing business behavior not specified in the database design.

---

---

## 20a. `payment_method` Fields — Explicitly Unrestricted (for now)

`payment_method` appears on `CustomerPayment`, `SupplierPayment`, and `Expense`. `06_Database_Design.md` defines it as `VARCHAR, Required` on each (§15, §16, §18) with no enumerated set of allowed values anywhere in the approved design.

Accordingly, `payment_method` is implemented as a **plain, unrestricted `CharField`** — not a Django `Choices` enum — on all three models. This is a deliberate decision, not an oversight: introducing a fixed choice list (e.g. `CASH`, `BANK_TRANSFER`, `CHEQUE`) would be inventing a business rule the approved documents don't specify. If the Business Rules or Functional Requirements documents later define a closed set of payment methods, this field should be converted to `Choices` at that time.

---

## 21. Model Constraints Summary

| Constraint | Applies to |
|---|---|
| `current_stock >= 0` | Product (CheckConstraint + service-layer locking, §16) |
| `current_purchase_cost >= 0` | Product |
| `current_sell_price >= 0` | Product |
| `minimum_stock >= 0` | Product |
| `quantity > 0` | PurchaseItem, SaleItem, InventoryAdjustment |
| `unit_cost >= 0` / `unit_price >= 0` | PurchaseItem / SaleItem |
| `discount_amount >= 0` | Sale only (no discount field on Purchase, PurchaseItem, or SaleItem — see §10, §11, §13) |
| `discount_amount <= subtotal_amount` | Sale (per `06_Database_Design.md` §24) |
| `total_amount = subtotal_amount - discount_amount` | Sale (per `06_Database_Design.md` §24) |
| `line_total >= 0` | PurchaseItem, SaleItem |
| `total_amount >= 0` | Purchase, Sale |
| `amount > 0` | CustomerPayment, SupplierPayment, Expense |
| exactly-one-of + uniqueness | TransactionCancellation (§19) |
| `name` unique | Category, Unit |
| `symbol` unique | Unit |

---

## 22. Foreign Key Delete Strategy (resolved — design issue #1)

**Principle** (not just a fixed list): any foreign key from a historical/transactional record to a master-data table, a parent transaction, or a user account uses `on_delete=PROTECT`. This preserves the invariant that historical transactions remain valid even if the referenced master-data row becomes inactive or someone attempts to delete it.

**Exception — parent-to-child ownership uses `CASCADE`, not `PROTECT`.** Where a row's FK points to its *exclusive owning parent* rather than to shared master data (i.e. the child has no meaning without that specific parent), `on_delete=CASCADE` is used instead. This applies only to `PurchaseItem → Purchase` and `SaleItem → Sale` (see §10, §12). The distinguishing test: would any other row ever reference this same target for a different purpose? Master data (Product, Customer, Supplier, Category, Unit), parent transactions being cancelled (§19), and user accounts (§22a) all fail that test — they're shared or independently meaningful, so `PROTECT`. Line items fail it the other way — they belong to exactly one parent and nothing else — so `CASCADE`.

Concretely, `PROTECT` applies to:

```text
Category → Product
Unit → Product
Supplier → Purchase
Customer → Sale
Product → PurchaseItem      -- added
Product → SaleItem          -- added
Product → InventoryAdjustment -- added
Customer → CustomerPayment  -- added
Supplier → SupplierPayment  -- added
Sale → TransactionCancellation      -- added, see §19
Purchase → TransactionCancellation  -- added, see §19
```

`CASCADE` applies to:

```text
Purchase → PurchaseItem   -- see §10
Sale → SaleItem           -- see §12
```

Any new transactional model introduced later that references master data must follow the same principle by default — this should be treated as a standing rule, not something re-decided per model.

---

## 22a. Foreign Key Delete Strategy — User Audit Fields (resolves design issue #4 from this round)

The original design documents specify `created_by`, `completed_by`, `cancelled_by`, and `recorded_by` as FKs to `settings.AUTH_USER_MODEL`, but neither `06_Database_Design.md` nor the original `07_Django_Model_Design.md` states an `on_delete` behavior for them. This is now decided explicitly:

**Decision: `on_delete=PROTECT` for all User audit FKs, with `null=False` where the action is mandatory (`created_by`) and `null=True` where the lifecycle stage may not have happened yet (`completed_by`, `cancelled_by`).**

Rationale:
- These fields exist for auditability (§4, §31 of the database design) — knowing *who* completed or cancelled a transaction is a business requirement, not incidental metadata. `SET_NULL` would silently destroy that audit trail the moment a user account is removed, which directly contradicts the auditability principle.
- `CASCADE` is unacceptable — deleting a `User` must never cascade-delete `Purchase`, `Sale`, `CustomerPayment`, etc. Historical business records must survive regardless of what happens to the user account.
- `PROTECT` is therefore the correct choice: it's consistent with the master-data protection principle in §22, and it forces an explicit decision (deactivate the Django user via `is_active=False`, never delete it) rather than allowing an accidental data-integrity gap.

This applies uniformly to:
```text
created_by   (Purchase, Sale, InventoryAdjustment, Expense)
completed_by (Purchase, Sale)
cancelled_by (Purchase, Sale, TransactionCancellation)
recorded_by  (CustomerPayment, SupplierPayment)
```

Practical implication: Django user accounts in this system should be deactivated (`is_active=False`), never deleted, once they have any audit-trail history — matching the same "deactivate, don't delete" pattern already established for Category/Unit/Product/Supplier/Customer in §22/§24.

---

## 23. Model-Validation / DB-Constraint / Service-Layer Split (resolved — design issue #10)

| Layer | Used for | Examples in this system |
|---|---|---|
| **PostgreSQL constraint** | Invariants that must hold no matter the code path (manual SQL, admin panel, buggy migration). Cannot depend on another row's live value. | `amount > 0`, `quantity > 0`, `current_stock >= 0`, TransactionCancellation exactly-one/uniqueness |
| **Django `Model.clean()`** | Single-record validation that needs no cross-row query or locking. | `Sale.payment_type == CREDIT` requires `customer` set |
| **Service layer** | Anything involving multiple rows, concurrency, state transitions, or values computed from other tables. | stock deduction, stock-floor check, status transitions, totals snapshotting, balance calculation |

**Heuristic**: if a rule can be violated by two concurrent requests racing each other, it cannot live only in `clean()` — it needs `select_for_update()` in a service method, ideally backed by a DB constraint as a backstop.

---

## 24. Foreign Key Delete Strategy — Historical Integrity

Historical transactions must remain valid even if referenced records become inactive. This is why `is_active` flags exist on master-data models rather than deletion — actual row deletion of referenced master data is blocked by `PROTECT` (§22), and "removal" from active use is handled by toggling `is_active`, not by deleting the row.

---

## 25. Model Methods — Service Layer Only

The following business operations shall be implemented in the service layer, not in model `save()` methods, and shall execute inside database transactions with row-level locking where they touch `current_stock`, `status`, or balances:

```text
complete_sale()
cancel_sale()
complete_purchase()
cancel_purchase()
apply_inventory_adjustment()
record_customer_payment()
record_supplier_payment()
```

Each of these must, at minimum:
1. Open `transaction.atomic()`.
2. Lock the relevant row(s) with `select_for_update()`.
3. Validate the operation is legal (state transition allowed, stock sufficient, etc.).
4. Perform all writes (status, totals, stock, audit fields) together.
5. Never leave the system in a state where a Sale/Purchase is COMPLETED but stock/totals weren't updated, or vice versa.

---

## 26. Django Migration Outcome

The final Django migrations shall create:

```text
Category
Unit
Product
Supplier
Customer
Purchase
PurchaseItem
Sale
SaleItem
CustomerPayment
SupplierPayment
InventoryAdjustment
Expense
TransactionCancellation
```

with all foreign keys, indexes, constraints (§21), and audit relationships (§4) as defined in this revised document.

---

## 27. Service Layer Responsibility

Business workflows shall be implemented in dedicated services rather than model save methods.

Examples:
- Inventory updates (locked, atomic)
- Stock validation (stock-floor rule, §16)
- Sale completion (state machine, §17; totals snapshot, §12)
- Purchase completion (state machine, §17; totals snapshot, §10)
- Transaction cancellation (state machine, §17; DB constraint backstop, §19)
- Balance calculations (derived, never cached, §16.1)
- Payment processing

Models remain responsible for:
- Data structure
- Relationships (including `PROTECT` strategy, §22)
- Single-row validation
- Constraints

Business process orchestration, concurrency control, and state-transition enforcement belong to the service layer.

---

## 28. Open Business Decisions (must remain open — resolves design issue #6)

Note: `06_Database_Design.md` §40 has already settled the discount model for V1 — sale-level discounts only, stored as `Sale.subtotal_amount`/`discount_amount`/`total_amount`, with no discount field on `SaleItem`, `Purchase`, or `PurchaseItem`. This is no longer an open decision and is reflected in §10, §11, §12, and §13 above.

The following remain genuinely open and must not be invented during implementation:

- **Inventory costing method**: FIFO, weighted-average, or another method for `current_purchase_cost` / cost-of-goods calculations.
- Any future extension of discounts to purchases or to individual line items, should that ever be requested — out of scope for V1 per the database design.

The model layer only stores the fields specified in the approved database design; it does not encode any costing algorithm. Implementation must wait for the Business Rules or Functional Requirements documents to specify these where still open.

---
## 29. Currency

- All monetary fields use Syrian Pound (SYP).
- Currency is fixed at the system level in V1.
- No currency field is required on individual transactions or monetary records.
- Django monetary fields store the numeric amount only; currency is understood to be SYP.

---

## 30. Final Design Decision

The Django model architecture defined in this revised document is considered the direct implementation blueprint for the approved V1 database design, superseding the original `07_Django_Model_Design.md`.

No additional business behavior shall be introduced during implementation unless the Business Requirements, Functional Requirements, Business Rules, or Database Design documents are updated accordingly.
---



**Next step**: proceed to Django model code generation from this document, followed by migrations, then the service layer (§17, §25, §27), then tests.
