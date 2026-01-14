# PySpark 3 - Nulls and Aggregations

---

## 1. The Foundation: SparkSession and Lazy Evaluation (Repetation, since highly IMP)

Every journey begins with the **SparkSession**, the mandatory entry point for any Spark application. When working locally, setting the master to `local[*]` allows Spark to utilise all logical cores on your machine. 

A core concept to grasp is **Lazy Evaluation**. Think of Spark like a **Chef in a Restaurant**. The **Transformations** (like `filter` or `select`) are the recipes—they describe how to prepare a dish, but no cooking happens yet. The **Action** (like `.show()`, `.count()`, or `.write()`) is when the customer places an order; only then does the chef follow the recipe to produce the final meal.

---

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

## 4. Architecture: Joins, Unions, and Performance

Combining datasets and optimising how they sit on a cluster is what separates beginners from experts.

### **Joins and Unions**
PySpark supports standard **Inner** and **Left Outer** joins. For complex logic, you can use cascading conditions with brackets and bitwise operators (`&` for AND, `|` for OR). 
When combining datasets with different column sequences, **`unionByName`** is your best friend—it automatically aligns jumbled columns as long as the names match.

### **Performance Tuning**
Understanding how data is partitioned across executors is vital. 
*   **Repartition:** Increases or decreases partitions by shuffling data—ideal for partitioning by a specific column to ensure similar data (like `dept_id`) sits together.
*   **Coalesce:** A more efficient way to *reduce* partitions because it avoids a full data shuffle.