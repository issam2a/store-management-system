# StoreFlow — UI Design Specification

**Document Status:** Draft — Design Direction Approved
**Product:** StoreFlow
**Application Type:** Retail Store Management System
**Primary UI Languages:** Arabic / English
**Layout Modes:** RTL / LTR
**Theme:** Dark Glassmorphism
**Design Target:** Modern commercial SaaS application

---

# 1. Design Vision

StoreFlow is a modern Store Management System designed for small and medium-sized retail businesses.

The interface should feel like a **premium commercial SaaS product**, while remaining practical for daily business operations.

The design prioritizes:

1. Readability
2. Speed of interaction
3. Clear information hierarchy
4. Consistent workflows
5. Professional visual identity
6. Arabic RTL support
7. English LTR support
8. Subtle visual depth
9. Minimal but meaningful animation

The application should not feel like a generic admin template.

---

# 2. Brand Identity

## Product Name

**StoreFlow**

The technical repository name remains:

`store-management-system`

The user-facing product name is:

**StoreFlow**

Arabic brand rendering may be:

**ستورفلو**

The brand name should remain visually recognizable in both languages.

---

# 3. Design Style

## Primary Style

**Dark Glassmorphism**

The interface combines:

* Dark green/charcoal backgrounds
* Translucent glass surfaces
* Backdrop blur
* Subtle borders
* Sage-green accents
* Soft shadows
* Controlled glow effects
* High-contrast typography

Glassmorphism should be used selectively.

It should provide visual depth without reducing usability.

---

# 4. Color System

## Brand Palette

The primary brand palette is:

| Name       | Hex       | Purpose                           |
| ---------- | --------- | --------------------------------- |
| Light Sage | `#EDF1D6` | Primary light text, highlights    |
| Sage       | `#9DC08B` | Secondary accent                  |
| Green      | `#609966` | Primary actions and active states |
| Deep Green | `#40513B` | Brand color, navigation accents   |

---

## Dark UI Foundation

Additional colors are introduced specifically for the dark interface.

| Name            | Value                       | Purpose                     |
| --------------- | --------------------------- | --------------------------- |
| Background      | `#0F1510`                   | Main application background |
| Surface         | `#141C16`                   | Solid dark surfaces         |
| Glass           | `rgba(64, 81, 59, 0.45)`    | Glass panels                |
| Glass Highlight | `rgba(157, 192, 139, 0.10)` | Subtle green highlight      |
| Glass Border    | `rgba(237, 241, 214, 0.10)` | Glass boundaries            |
| Primary Text    | `#EDF1D6`                   | Main text                   |
| Secondary Text  | `#B8C4B3`                   | Secondary information       |

---

# 5. Color Usage Rules

The colors must have defined roles.

### `#609966`

Primary action color.

Used for:

* Add
* Save
* Create
* Complete
* Confirm
* Primary navigation states
* Important interactive elements

### `#9DC08B`

Secondary accent.

Used for:

* Highlights
* Secondary states
* Icons
* Chart accents
* Hover states
* Decorative details

### `#40513B`

Deep brand color.

Used for:

* Strong navigation elements
* Dark green surfaces
* Brand accents
* Selected/active visual states

### `#EDF1D6`

Used primarily for:

* Headings
* Important text
* Icons
* High-contrast elements

It should not be used as the main page background in the dark theme.

---

# 6. Semantic Colors

Business status colors are independent from the brand palette.

| Status  | Purpose                                  |
| ------- | ---------------------------------------- |
| Success | Completed / successful operations        |
| Warning | Low stock / pending / attention required |
| Danger  | Cancelled / failed / destructive actions |
| Info    | Informational states                     |
| Neutral | Draft / inactive / unspecified           |

Semantic colors must remain recognizable even when the brand palette is green.

For example:

* Completed → Green
* Pending → Amber
* Cancelled → Red
* Draft → Gray

---

# 7. Background

The application should use a very dark green/charcoal base.

Recommended:

```css
background: #0F1510;
```

The background may contain a subtle animated atmosphere using the StoreFlow sage palette.

## Background Animation

The background may include:

* Extremely slow gradient movement
* Soft blurred green shapes
* Low-opacity radial gradients
* Subtle atmospheric glow

Animation duration should generally be around:

**20–40 seconds**

The animation must remain subtle.

The user should perceive depth rather than consciously watching an animation.

---

# 8. Glassmorphism

Glass surfaces should use:

* Transparency
* Backdrop blur
* Thin borders
* Soft shadows
* Very subtle green highlights

Example conceptual styling:

```css
background: rgba(64, 81, 59, 0.45);
backdrop-filter: blur(18px);
-webkit-backdrop-filter: blur(18px);
border: 1px solid rgba(237, 241, 214, 0.10);
```

Glassmorphism should primarily be used for:

* Sidebar
* Top navigation
* KPI cards
* Dashboard widgets
* Modals
* Dropdowns
* Notifications

---

# 9. Data-Dense Areas

Glassmorphism must not compromise usability.

Data-heavy interfaces such as:

* Product tables
* Sales tables
* Purchase tables
* Inventory tables
* Payment tables

should use darker, more opaque surfaces where necessary.

Priority:

**Readability > Glass effect**

---

# 10. Main Application Layout

The desktop application uses:

```text
Sidebar + Topbar + Main Content
```

Conceptually:

```text
┌─────────────────────────────────────────────────────┐
│                    TOPBAR                           │
├───────────────┬─────────────────────────────────────┤
│               │                                     │
│    SIDEBAR    │           MAIN CONTENT              │
│               │                                     │
│               │                                     │
│               │                                     │
└───────────────┴─────────────────────────────────────┘
```

---

# 11. Sidebar

The sidebar contains the main application navigation.

## Navigation

### Overview

* Dashboard

### Management

* Products
* Inventory
* Sales
* Purchases

### Relationships

* Customers
* Suppliers

### Financial

* Payments
* Expenses

### Insights

* Reports
* Analytics

### System

* Settings
* Users

The sidebar should support collapsing.

---

# 12. RTL Sidebar Behavior

English:

```text
Sidebar → Left
Content → Right
```

Arabic:

```text
Content → Left
Sidebar → Right
```

The layout should use CSS logical properties wherever practical instead of hard-coded left/right positioning.

Examples:

```css
margin-inline-start
margin-inline-end
padding-inline-start
padding-inline-end
inset-inline-start
inset-inline-end
```

---

# 13. Topbar

The topbar should contain:

* StoreFlow branding
* Global search
* Notifications
* Language switcher
* User profile
* Optional theme control

The topbar should use a subtle glass surface.

---

# 14. Language Switcher

Supported languages:

```text
English
العربية
```

The language switcher must use Django's internationalization system.

The interface automatically changes:

```html
lang="en"
dir="ltr"
```

or:

```html
lang="ar"
dir="rtl"
```

No separate duplicated interface should be created for Arabic and English.

---

# 15. Dashboard

The dashboard is the primary landing page.

## KPI Cards

Initial KPIs:

* Today's Sales
* Monthly Revenue
* Net Profit
* Inventory Value
* Outstanding Customer Debt
* Outstanding Supplier Balance

Cards should be visually compact rather than excessively large.

Each card may contain:

* Metric name
* Current value
* Comparison/trend
* Small icon
* Optional sparkline

---

# 16. Dashboard Visual Hierarchy

Recommended structure:

```text
Dashboard

[ Today's Sales ]
[ Revenue       ]
[ Net Profit    ]
[ Inventory     ]

[              Sales Trend              ]

[ Top Products ]     [ Inventory Status ]

[              Recent Sales             ]

[              Low Stock                ]
```

The exact grid can be adjusted during implementation based on screen size.

---

# 17. Products

The Products page should prioritize operational efficiency.

Main elements:

* Page title
* Search
* Filters
* Add Product button
* Product table
* Pagination

Product table:

| Product | Category | Stock | Purchase Price | Selling Price | Status |
| ------- | -------- | ----: | -------------: | ------------: | ------ |

Actions:

* View
* Edit
* More

---

# 18. Sales

The Sales interface should prioritize speed.

Primary workflow:

```text
Search Product
      ↓
Add to Cart
      ↓
Review Items
      ↓
Select Customer
      ↓
Apply Discount
      ↓
Select Payment
      ↓
Complete Sale
```

The interface should make the **Complete Sale** action visually obvious.

---

# 19. Purchases

Purchase workflow:

```text
Select Supplier
      ↓
Add Products
      ↓
Review Quantities / Prices
      ↓
Calculate Total
      ↓
Complete Purchase
```

Draft and completed states should be visually distinct.

---

# 20. Inventory

Inventory should provide immediate visibility into stock.

Display:

* Current stock
* Low stock
* Out of stock
* Inventory adjustments
* Recent inventory activity

Stock status should be immediately recognizable through semantic status indicators.

---

# 21. Reports

Reports answer:

**"What happened?"**

The visual design should prioritize:

* Detailed tables
* Filters
* Date ranges
* Export actions
* Operational information

Reports should be information-dense but readable.

---

# 22. Analytics

Analytics answer:

**"Why did it happen?"**

and:

**"What should I focus on?"**

Analytics pages should emphasize:

* KPIs
* Trends
* Rankings
* Profitability
* Product performance
* Category performance
* Supplier performance
* Inventory performance

Charts should support decision-making rather than exist purely as decoration.

---

# 23. Buttons

Create a consistent button hierarchy.

## Primary

Used for:

* Add
* Create
* Save
* Complete
* Confirm

Visual:

* StoreFlow green
* High contrast
* Slight hover elevation

## Secondary

Used for:

* Back
* Cancel
* Filter
* Secondary actions

## Danger

Used for:

* Cancellation
* Destructive operations

## Icon Buttons

Used for:

* Edit
* View
* Delete
* More
* Close

Icons should always have tooltips where their meaning is not obvious.

---

# 24. Forms

Forms should use:

* Clear labels
* Consistent spacing
* Strong focus states
* Validation feedback
* Required indicators
* Helpful error messages

Inputs should use dark surfaces with sufficient contrast.

Focus states should use the StoreFlow green accent.

---

# 25. Tables

Tables are a core component of StoreFlow.

They must support:

* Search
* Filtering
* Sorting
* Pagination
* Status badges
* Row actions
* Numeric alignment

Currency and numerical values should be visually aligned for easy comparison.

Arabic and English tables must remain readable in both directions.

---

# 26. Cards

Cards should use restrained glassmorphism.

Characteristics:

* Rounded corners
* Subtle border
* Backdrop blur where appropriate
* Low-opacity background
* Soft shadow
* Clear hierarchy

Avoid excessive nested cards.

---

# 27. Modals and Drawers

Use glassmorphism for:

* Product details
* Confirmation dialogs
* Quick actions
* Notifications

Modals must maintain strong contrast and clear primary/secondary actions.

Destructive confirmation dialogs should clearly communicate consequences.

---

# 28. Typography

Typography should prioritize:

* Excellent Arabic readability
* Excellent English readability
* Clear hierarchy
* Numerical readability

The final font choice should support both Arabic and Latin scripts well.

Recommended evaluation criteria:

* Arabic letterform quality
* Number readability
* Dashboard density
* Weight availability
* Screen rendering

Font sizes should remain conservative because the application is data-heavy.

---

# 29. Border Radius

Use a consistent radius system.

Recommended starting scale:

```text
Small:   8px
Medium:  12px
Large:   16px
XL:      20px
```

Avoid excessive pill-shaped elements except for:

* Status badges
* Compact filters
* Tags

---

# 30. Shadows

Shadows should be soft and subtle.

Avoid heavy black shadows.

Glass surfaces should obtain depth primarily through:

* Transparency
* Blur
* Border
* Contrast
* Very soft shadow

---

# 31. Animation

Animation should improve perceived responsiveness.

Recommended:

* Sidebar transitions
* Button hover
* Modal transitions
* Toast notifications
* Chart entrance animations
* KPI number transitions
* Subtle background animation

Avoid:

* Constant movement
* Large bouncing elements
* Excessive page transitions
* Distracting animated tables

Recommended interaction duration:

```text
150–250ms
```

Background animation:

```text
20–40 seconds
```

---

# 32. Accessibility

The design must maintain:

* Strong color contrast
* Visible keyboard focus
* Readable text
* Clear error states
* Non-color-only status communication
* Accessible buttons
* Appropriate labels

Glass effects must never reduce text readability.

---

# 33. Responsive Strategy

Primary target:

**Desktop / Laptop**

Secondary support:

**Tablet**

Mobile support should focus on essential workflows rather than attempting to reproduce the entire desktop interface on a small screen.

---

# 34. Design Principles

The StoreFlow interface follows these principles:

### 1. Business first

Every visual element should support a business task.

### 2. Data clarity

Users should understand numbers immediately.

### 3. Consistency

The same action should look the same everywhere.

### 4. Controlled glassmorphism

Glass adds depth; it must never interfere with usability.

### 5. Subtle animation

Motion should communicate state rather than demand attention.

### 6. RTL from the beginning

Arabic is not an afterthought.

### 7. Reusable components

Build once and reuse throughout the application.

### 8. Portfolio quality

The application should demonstrate professional frontend architecture and UX thinking, not simply a collection of CRUD pages.

---

# 35. Implementation Strategy

The frontend should be implemented progressively.

## Stage 1 — Foundation

Build:

* Base layout
* Design tokens
* Global CSS
* Typography
* Sidebar
* Topbar
* Language switcher
* RTL/LTR behavior
* Background animation

## Stage 2 — Components

Build reusable:

* Buttons
* Cards
* Inputs
* Selects
* Tables
* Badges
* Alerts
* Modals
* Dropdowns

## Stage 3 — Dashboard

Implement the complete dashboard using the design system.

## Stage 4 — Operational Pages

Implement:

* Products
* Categories
* Units
* Suppliers
* Customers

## Stage 5 — Transactions

Implement:

* Purchases
* Sales
* Payments
* Inventory Adjustments
* Transaction Cancellation

## Stage 6 — Intelligence

Connect:

* Reports
* Analytics

to the existing backend services.

---

# 36. Design Acceptance Criteria

The design is considered successful when:

* The interface immediately looks like a professional retail SaaS product.
* Arabic and English feel equally native.
* RTL does not look like a mirrored afterthought.
* Glassmorphism adds depth without reducing readability.
* Tables remain highly usable.
* Primary actions are obvious.
* Dashboard information is understandable at a glance.
* The interface remains visually consistent across all modules.
* Animation is subtle enough for daily business use.
* The design can be implemented using reusable Django templates and CSS components.

---

# 37. Current Design Direction

**Brand:** StoreFlow

**Style:** Dark Glassmorphism

**Primary Palette:**

```text
#EDF1D6
#9DC08B
#609966
#40513B
```

**Foundation:**

```text
#0F1510
#141C16
```

**Languages:**

```text
English — LTR
Arabic  — RTL
```

**Layout:**

```text
Sidebar + Topbar + Main Content
```

**Animation:**

```text
Subtle animated atmospheric background
```

**Priority:**

```text
Usability
↓
Readability
↓
Consistency
↓
Visual polish
↓
Decoration
```

This hierarchy should guide all future frontend decisions.
