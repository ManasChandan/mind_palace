# The PySpark Essentials

## Table of Contents
1. [Initialising the SparkSession](#spark-session)
2. [Creating DataFrames and Lazy Evaluation](#data-and-lazy-eval)
3. [Designing and Managing Schema](#schema-definition)
4. [Basic Structured Transformations](#basic-structured-transformations)
5. [Advanced Column Operations](#advanced-col-operations)

---

<div id="spark-session"></div>

## 1. Initialising the SparkSession
The **SparkSession** is the primary driver process and the mandatory **entry point** for any Spark application. To create one, you use the `SparkSession.builder` method from the `pyspark.sql` module.

When working in a local environment, setting the master to **`local[*]`** is a standard configuration; the `*` allows Spark to open worker threads equal to the number of **logical cores** on your machine. Once active, Spark provides an **Application UI** (usually at `localhost:4040`), which allows you to monitor query executions for structured APIs. 

**PLEASE NOTE** : The Spark UI doesn't pop up (in many cases) untill you call an first action. The reason, only after calling an action spark registers your app to start the main evaluation.  

```python
from pyspark.sql import SparkSession

# Standard SparkSession creation
spark = SparkSession.builder \
    .appName("SparkIntroduction") \
    .master("local[*]") \
    .getOrCreate()
```

---
<div id="data-and-lazy-eval"></div>

## 2. Creating DataFrames and Lazy Evaluation
To create your first DataFrame, you can use the **`spark.createDataFrame()`** method, passing in your raw data (often a list of lists) and a schema. 

A core concept to grasp is **Lazy Evaluation**. PySpark does not execute transformations (like `filter` or `select`) immediately; it builds a logical plan. Execution only occurs when an **Action** is called, such as:
*   **`.show()`**: Displays the data in the console.
*   **`.write()`**: Saves the data to an output location (e.g., as a CSV).
*   **`.count()`**: Returns the number of rows.

---
<div id="schema-definition"></div>

## 3. Defining and Managing Schemas
Spark internally stores schemas using **`StructType`** and **`StructField`**. Each field defines the column name, data type (e.g., `StringType`, `IntegerType`), and whether it is **nullable**.

While you can manually define these types, Spark also allows the use of **schema strings** (e.g., `"age INT, name STRING"`). Spark uses an internal utility to **implicitly convert** these strings into native Spark data types.

```python
# Visualising a schema structure
# root
#  |-- emp_id: string (nullable = true)
#  |-- age: integer (nullable = true)
#  |-- salary: double (nullable = true)
```

---
<div id="basic-structured-transformations"></div>

## 4. Basic Structured Transformations
To manipulate data, PySpark provides several methods to select and modify columns:

*   **`select`**: Used to project specific columns.
*   **`expr`**: Allows you to write **SQL-like expressions** for column manipulations.
*   **`selectExpr`**: A powerful combination that allows you to perform selections and expressions (like **aliasing** or **casting**) in a single step without explicitly calling the `expr` function.
*   **`cast`**: Changes the data type of a column, such as converting a string to an integer or double.

```python
# Using selectExpr for clean transformations
df_final = df.selectExpr(
    "emp_id AS employee_id", 
    "cast(age AS int) AS age", 
    "salary"
)
```

---

<div id="advanced-col-operations"></div>

## 5. Advanced Column Operations
For more complex data engineering tasks, you will frequently use the following APIs:

*   **`withColumn`**: Used to add a new column or overwrite an existing one.
*   **`lit()`**: Short for "literal," this function is required to add a column with a **static or constant value**.
*   **`withColumnRenamed`**: A dedicated method for changing column names, which is also useful for handling **names with spaces**.
*   **`drop`**: Removes one or more columns from the DataFrame.
*   **`limit`**: Restricts the result set to a specific number of records, which is useful for testing or sampling.

### 💡 Production Tip: Adding Multiple Columns
Instead of chaining multiple `.withColumn()` calls, which can be verbose, you can use the **`.withColumns()`** method. By passing a **dictionary** of column names and their corresponding logic, you can add multiple columns in a single, efficient operation.

```python
from pyspark.sql.functions import lit

# Bulk adding columns using a dictionary
new_cols = {
    "tax": df["salary"] * 0.2,
    "status": lit("active"),
    "updated_by": lit("system_user")
}

df_enhanced = df.withColumns(new_cols)
```

---

### Summary Table: Transformations vs. Actions

| Type | Examples | Purpose |
| :--- | :--- | :--- |
| **Transformations** | `select`, `filter`, `withColumn`, `drop` | Defines the transformation logic (Lazy). |
| **Actions** | `show`, `count`, `write`, `collect` | Triggers computation and returns results. |

**Analogy for Understanding Spark Execution:**
Think of Spark like a **Chef in a Restaurant**. The **Transformations** are the recipes written in a book—they describe exactly how to prepare a dish, but no cooking happens yet. The **Action** is when a customer places an order; only at that moment does the chef follow the recipe to produce the final meal.