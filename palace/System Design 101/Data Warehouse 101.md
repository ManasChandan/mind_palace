## 📑 Table of Contents

<ul>
  <li><a href="#what-is-data-warehousing">1. What is data warehousing?</a></li>
  <li><a href="#oltp-and-olap">2. What are OLTP and OLAP, and how do they relate to data warehousing?</a></li>
  <li><a href="#etl-elt">3. What are ETL, ELT, and other data loading strategies?</a></li>
  <li><a href="#measures-attributes-grains">4. What are measures, attributes, and grains?</a></li>
  <li><a href="#facts-and-dimensions">5. What are facts and dimensions?</a></li>
  <li><a href="#dimension-types">6. Conformed, junk, degenerated, and role-playing dimensions</a></li>
  <li><a href="#scd">7. Slowly Changing Dimensions (SCD 1, 2, 3)</a></li>
  <li><a href="#fact-types">8. Types of fact tables</a></li>
  <li><a href="#star-vs-snowflake">9. Star schema vs Snowflake schema (and OLAP)</a></li>
  <li><a href="#early-late">10. Early arriving facts and late arriving dimensions</a></li>
</ul>

---

<div id="what-is-data-warehousing"></div>

## 1. What is data warehousing?

**Data warehousing** is about **collecting data from many systems, cleaning it up, and storing it in a way that makes reporting and analysis fast and easy**.

Think of it like this:

* Your **operational systems** (apps, websites, billing systems) are busy *running the business*
* Your **data warehouse** is built to *understand the business*

### Simple example

An e-commerce company has:

* Order system
* Payment system
* Customer support system

Each system has its own database.  
A **data warehouse** pulls data from all of them and answers questions like:

* “How much did we sell last month by region?”
* “Which products are returned the most?”
* “How many new customers did marketing bring in?”

👉 The warehouse is **read-heavy**, historical, and optimized for analytics—not transactions.

---

<div id="oltp-and-olap"></div>

## 2. What are OLTP and OLAP, and how do they relate to data warehousing?

### OLTP – Online Transaction Processing

This is where **day-to-day business happens**.

**Characteristics**

* Lots of small reads & writes
* Many users at the same time
* Data is constantly changing
* Highly normalized tables

**Examples**

* Placing an order
* Updating a customer address
* Making a payment

**Typical databases**

* MySQL, PostgreSQL, Oracle, SQL Server

---

### OLAP – Online Analytical Processing

This is about **analysis and reporting**.

**Characteristics**

* Fewer users
* Heavy queries (scans millions/billions of rows)
* Mostly reads
* Historical data

**Examples**

* Sales trend over 5 years
* Revenue by product category and country
* Monthly active users

---

### Relationship to data warehousing

* **OLTP systems feed the data warehouse**
* **Data warehouse supports OLAP**

You *can* run reports on OLTP systems, but:

* It slows down the app
* Queries are complex
* Results are inconsistent

That’s why we separate them.

---

<div id="etl-elt"></div>

## 3. What are ETL, ELT, and other data loading strategies?

### ETL – Extract, Transform, Load

1. Extract data from source systems  
2. Transform it **before** loading  
3. Load clean data into the warehouse  

**Used when**

* Warehouse is expensive
* Transformations are heavy
* Older architectures

**Example**

* Clean dates
* Convert currencies
* Join tables before loading

---

### ELT – Extract, Load, Transform

1. Extract data  
2. Load raw data into warehouse  
3. Transform **inside** the warehouse  

**Used when**

* Cloud warehouses (Snowflake, BigQuery, Redshift)
* Storage + compute is cheap
* Want raw data preserved

**Most modern systems use ELT**

---

### Other strategies

* **Batch loading** – daily/hourly loads
* **Streaming** – near real-time (Kafka, Kinesis)
* **CDC (Change Data Capture)** – only changes are loaded
* **Full refresh** – reload everything (simple but expensive)

---

<div id="measures-attributes-grains"></div>

## 4. What are measures, attributes, and grains?

### Grain (MOST IMPORTANT)

**Grain = what one row represents**

Everything else depends on this.

**Example**

* Grain: *one row per order line*
* Grain: *one row per customer per day*

If the grain is unclear, the table is broken.

---

### Measures

**Numeric values you aggregate**

Examples:

* Sales amount
* Quantity sold
* Discount
* Profit

You usually **SUM, AVG, COUNT** measures.

---

### Attributes

**Descriptive fields**

Examples:

* Product name
* Customer city
* Order status
* Category

Attributes are used for **filtering, grouping, slicing**.

---

<div id="facts-and-dimensions"></div>

## 5. What are facts and dimensions?

### Fact tables

* Store **measures**
* At a defined **grain**
* Contain foreign keys to dimensions
* Usually very large

**Example: Sales Fact**

| Date | Product | Store | Revenue | Quantity |
| ---- | ------- | ----- | ------- | -------- |

---

### Dimension tables

* Store **context / description**
* Smaller
* Change slowly

**Example: Product Dimension**

| Product Key | Name | Category | Brand |

---

👉 Facts answer **“how much / how many”**  
👉 Dimensions answer **“by what”**

---

<div id="dimension-types"></div>

## 6. Conformed, junk, degenerated, and role-playing dimensions

### Conformed dimensions

**Shared dimensions used across multiple fact tables**

Example:

* `Date` used by Sales, Inventory, Returns

This allows **cross-fact analysis**:

> Sales vs Returns by Month

---

### Junk dimensions

Combine **low-cardinality flags** into one dimension.

Example flags:

* IsPromo (Y/N)
* IsOnlineOrder (Y/N)
* IsGift (Y/N)

Instead of many columns in fact → one **junk dimension**

---

### Degenerated dimensions

Dimensions **without a dimension table**

Example:

* Order ID
* Invoice Number

They live directly in the fact table because:

* No additional attributes
* Used for drill-down

---

### Role-playing dimensions

Same dimension used in **different roles**

Example: Date dimension

* Order Date
* Ship Date
* Delivery Date

Same table, multiple foreign keys.

---

<div id="scd"></div>

## 7. Slowly Changing Dimensions (SCD 1, 2, 3)

### SCD Type 1 – Overwrite

* Old value is lost
* No history

**Example**  
Customer changes city → update city

**Use when**

* Corrections
* History not important

---

### SCD Type 2 – Full history

* New row for every change
* Start date / end date
* Most common

**Example**  
Customer moves cities:

* Old row expires
* New row inserted

Allows:

> “Sales when customer lived in Bangalore”

---

### SCD Type 3 – Limited history

* Store current + previous value

**Example**  
Columns:

* Current City
* Previous City

Rarely used.

---

<div id="fact-types"></div>

## 8. Types of fact tables

### Transactional fact

* One row per transaction
* Most detailed

Example:

* Each order line

---

### Periodic snapshot fact

* One row per time period
* Summarized

Example:

* Daily account balance
* Monthly inventory

---

### Point-in-time fact

* Snapshot at a specific moment

Example:

* Customer status on month-end

---

### Accumulating snapshot fact

* Tracks lifecycle with multiple dates

Example: Order lifecycle

* Order Date
* Ship Date
* Delivery Date
* Payment Date

Row is updated as process progresses.

---

### Factless fact table

* No numeric measures
* Records events or coverage

Examples:

* Student attendance
* Promotion eligibility

Counts come from **counting rows**.

---

<div id="star-vs-snowflake"></div>

## 9. Star schema vs Snowflake schema (and OLAP)

### Star schema

* One fact table
* Directly connected to dimensions
* Simple joins
* Fast queries

⭐ **Preferred for OLAP**

---

### Snowflake schema

* Dimensions are normalized
* Dimension tables link to other dimension tables
* More joins
* Harder to query

❄️ Used when:

* Storage is tight
* Dimensions are very complex

---

### Fit with OLAP and DW

* **Star schema** = best for OLAP tools
* **Snowflake** = sometimes used, but slower
* Most warehouses aim for **star-like simplicity**

---

<div id="early-late"></div>

## 10. Early arriving facts and late arriving dimensions

### Early arriving facts

Fact arrives **before** dimension exists.

Example:

* Sales record arrives
* Customer record hasn’t loaded yet

**Solution**

* Create a **dummy dimension row**
* Update later

---

### Late arriving dimensions

Dimension arrives **after facts already exist**.

Example:

* Customer profile updated late

**Solution**

* Backfill foreign keys
* Use surrogate keys carefully

---
