# Nulls and Aggregations

---

## Table of Contents
1. [Lazy Evaluation](#lazy-eval)
2. [Refinement: Strings, Dates, and the "Dreaded" Null](#string-date-null)
3. [Analytical Power: Aggregations and Window Functions](#agg-window)
4. [Architecture: Joins, Unions, and Performance](#join-union-perf)

<div id="lazy-eval"></div>

## 1. The Foundation: SparkSession and Lazy Evaluation (Repetation, since highly IMP)

Every journey begins with the **SparkSession**, the mandatory entry point for any Spark application. When working locally, setting the master to `local[*]` allows Spark to utilise all logical cores on your machine. 

A core concept to grasp is **Lazy Evaluation**. Think of Spark like a **Chef in a Restaurant**. The **Transformations** (like `filter` or `select`) are the recipes—they describe how to prepare a dish, but no cooking happens yet. The **Action** (like `.show()`, `.count()`, or `.write()`) is when the customer places an order; only then does the chef follow the recipe to produce the final meal.

---
<div id="string-date-null"></div>

## 2. Refinement: Strings, Dates, and the "Dreaded" Null

Data in the wild is often messy, requiring surgical precision to clean.

### **Handling Strings and Nulls**
To handle missing data, you can use `na.drop()` to remove records entirely, though this is rarely ideal for production. A more robust approach is using the **`coalesce`** function alongside **`lit()`** (literals) to transform null values into meaningful defaults, such as "O" for "Others". For pattern-based cleaning, **`regexp_replace`** allows you to swap characters or patterns within a column effortlessly.

### **The Timeline: Dates and Timestamps**
Dates often enter the pipeline as strings. By using **`to_date`**, you can convert these into formal date types by providing the correct pattern (e.g., `yyyy-MM-dd`). 
*   **Bonus Tip:** Use `date_format` to extract specific components like the **Year** or even the **Timezone (UTC)**.

```python
# Cleaning data and formatting dates
from pyspark.sql.functions import coalesce, lit, to_date, date_format

df_clean = df.withColumn("gender", coalesce(df.new_gender, lit("O"))) \
             .withColumn("higher_date", to_date("higher_date", "yyyy-MM-dd")) \
             .withColumn("year", date_format("higher_date", "yyyy"))
```

---
<div id="agg-window"></div>

## 3. Analytical Power: Aggregations and Window Functions

Once the data is clean, the focus shifts to extracting insights.

### **Aggregations & The "Having" Clause**
Using `groupBy` and `agg`, you can calculate totals, averages, and counts. To mimic a SQL `HAVING` clause, simply chain a `.where()` filter after your aggregation logic.

### **Advanced Window Functions**
Window functions provide aggregations over a specific "window" of data. A classic use case is finding the **second highest salary** in each department:
1.  Define a **Window Specification** using `partitionBy` and `orderBy`.
2.  Apply `row_number()` to rank records within those groups.
3.  Filter for the specific rank.

```python
# Finding the second highest salary per department
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number, col

w_spec = Window.partitionBy("dept_id").orderBy(col("salary").desc())
df_ranked = df.withColumn("rn", row_number().over(w_spec)).where("rn == 2")
```

---
<div id="join-union-perf"></div>

## 4. Architecture: Joins, Unions, and Performance

Combining datasets and optimising how they sit on a cluster is what separates beginners from experts.

### **Joins and Unions**
PySpark supports standard **Inner** and **Left Outer** joins. For complex logic, you can use cascading conditions with brackets and bitwise operators (`&` for AND, `|` for OR). 
When combining datasets with different column sequences, **`unionByName`** is your best friend—it automatically aligns jumbled columns as long as the names match.

### **Performance Tuning**
Understanding how data is partitioned across executors is vital. 
*   **Repartition:** Increases or decreases partitions by shuffling data—ideal for partitioning by a specific column to ensure similar data (like `dept_id`) sits together.
*   **Coalesce:** A more efficient way to *reduce* partitions because it avoids a full data shuffle.

## 5. More on Joins

In Spark, there are **Logical Joins** (what you write in SQL) and **Physical Join Strategies** (how Spark actually moves the data).

### 1. Logical Join Types

These define *what* data you want to see.

| Join Type | Description |
| --- | --- |
| **Inner** | Returns rows where keys match in both tables. (Default) |
| **Left / Right Outer** | Returns all rows from one side plus matching rows from the other. |
| **Full Outer** | Returns all rows from both tables, filling with `NULL` where no match exists. |
| **Left Semi** | Returns rows from the Left table *only if* a match exists on the Right. (Doesn't keep Right columns). |
| **Left Anti** | Returns rows from the Left table *only if* there is **no** match on the Right. Great for finding "missing" data. |
| **Cross Join** | Cartesian product (every row joined with every row). **Danger:** Can crash your cluster if tables are large. |

### 2. Physical Join Strategies (The "Internal" Mechanics)

This is where the performance magic happens. Spark's optimizer (Catalyst) chooses these based on table size.

#### A. Broadcast Hash Join (BHJ)

* **How it works:** Spark sends the entire "small" table to every executor. The large table stays where it is.
* **Best for:** One small table (default threshold is **10MB**) and one large table.
* **Why it's fast:** **Zero Shuffle.** No data is moved across the network except the small table once.
* **Risk:** If the small table is actually big, you'll get an OOM on your executors.

#### B. Shuffle Sort-Merge Join (SMJ)

* **How it works:** 1. **Shuffle:** Both tables are hashed by the join key and moved so matching keys are on the same node.
2. **Sort:** Each partition is sorted.
3. **Merge:** Spark iterates through the sorted data and merges matches.
* **Best for:** Two large tables.
* **Why it's fast:** It is the most robust strategy. It can spill to disk if memory is low, so it rarely crashes.
* **Risk:** High network I/O due to the shuffle.

#### C. Shuffle Hash Join (SHJ)

* **How it works:** Similar to Shuffle Sort-Merge, but instead of sorting, it builds a Hash Table for each partition.
* **Best for:** Large tables where one side is significantly smaller than the other (but too big to broadcast) and keys are evenly distributed.
* **Risk:** If a single partition is too large to fit in memory as a hash table, it will OOM.

#### D. Broadcast Nested Loop Join (BNLJ)

* **How it works:** A nested loop (for each row in A, look at every row in B).
* **Best for:** Non-equi joins (e.g., `a.id > b.id`) or very small tables.
* **Risk:** Extremely slow. Use only as a last resort.

### 3. Comparison Table: Which Strategy to Use?

| Strategy | Hint | Condition | Efficiency | Handle Skew? |
| --- | --- | --- | --- | --- |
| **Broadcast** | `/*+ BROADCAST(table) */` | `==` (Equi-join) | **Best** | Yes |
| **Sort-Merge** | `/*+ MERGE(table) */` | `==` (Equi-join) | **Scalable** | Moderately |
| **Shuffle Hash** | `/*+ SHUFFLE_HASH(table) */` | `==` (Equi-join) | **Good** | No |
| **Nested Loop** | `/*+ SHUFFLE_REPLICATE_NL(table) */` | Any (>, <, !=) | **Worst** | No |

## 6. SHJ vs. Sort-Merge Join (SMJ)

In a **Shuffle Hash Join (SHJ)**, Spark builds a classic in-memory hash table (hash map) for one side of the join (the "build" side) within each partition.

To understand exactly what is stored, you have to look at the two-step process: **Shuffle** then **Hash**.

### 1. What is inside the Map?

For every partition, Spark takes the smaller of the two datasets (after shuffling them so that matching keys are on the same executor) and builds a map in memory.

* **The Key:** The **Join Key** (or a hash of the join key).
* **The Value:** A **list of rows** (or pointers to rows) that correspond to that specific join key.

Because multiple rows can have the same join key (one-to-many relationships), the hash map must store a collection of rows for every unique key.

### 2. How the process works (Step-by-Step)

1. **Shuffle Phase:** Both the left and right tables are partitioned based on the hash of the join key. This ensures that all rows with `ID=101` from Table A and Table B end up in the same partition on the same executor.
2. **Build Phase:** On each executor, Spark takes the *shuffled* data from the "build" table and constructs an **in-memory Hash Map**.
3. **Probe Phase:** Spark iterates through the other table (the "probe" table) row by row. For each row, it calculates the hash of the join key, looks it up in the Hash Map, and if a match is found, it joins the rows.

### 3. SHJ vs. Sort-Merge Join (SMJ)

This is where it gets interesting for performance:

| Feature | Shuffle Hash Join (SHJ) | Sort-Merge Join (SMJ) |
| --- | --- | --- |
| **Storage** | A **Hash Map** in memory. | Sorted blocks of data on disk/memory. |
| **CPU Cost** | Low (Hash lookups are ). | High (Sorting takes ). |
| **Memory Risk** | **High.** If the hash map for a partition exceeds available memory, you get an **OOM error**. | **Low.** Can "spill" to disk easily without crashing. |

### 4. Why does Spark prefer Sort-Merge by default?

Spark usually defaults to **Sort-Merge Join** because it is safer. In a **Shuffle Hash Join**, if your data has "Skew" (e.g., 80% of your rows have the same `user_id`), the Hash Map for that one partition will explode in size, exceeding the `spark.executor.memory`, and your job will fail.

**Sort-Merge** handles this by sorting the data. Even if the data is huge, it can read the sorted files sequentially from disk, which is much more stable than trying to cram everything into an in-memory map.

### When should you use SHJ?

You might manually force a Shuffle Hash Join using a hint:
`df1.hint("SHUFFLE_HASH").join(df2, "id")`

**Use it when:**

1. Your tables are too large to **Broadcast**.
2. But they are small enough that a single partition's "build side" fits comfortably in memory.
3. You want to avoid the expensive **Sort** step of the Sort-Merge Join to save CPU cycles.
