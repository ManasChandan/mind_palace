# Deep Dive: Reading Data and Optimizations using Spark UI

<div id="table-of-contents"></div>

## 📑 Table of Contents

* <a href="#learning-objectives">Key Learning Objectives</a>
* <a href="#columnar-formats">1. Why Columnar Data Formats are Useful</a>
* <a href="#parquet-read">2. Reading Parquet in PySpark</a>
* <a href="#orc-details">3. Working with ORC Files</a>
* <a href="#recursive-lookup">4. Recursive File Read</a>
* <a href="#json-handling">5. Handling JSON: Single vs. Multi-line</a>
* <a href="#from-json">6. from_json Applications</a>
* <a href="#to-json">7. to_json Applications</a>
* <a href="#nested-data">8. Explode and Struct Navigation</a>
* <a href="#spark-internals">Spark Internals: The "Hidden Cost" of Reading Data</a>
* <a href="#bad-records">Handling Bad Records (Read Modes)</a>
* <a href="#best-practices">Best Practices Implemented</a>

---

<div id="learning-objectives"></div>

## 🚀 Key Learning Objectives

* **Format Efficiency:** Understanding why Parquet and ORC outperform row-based formats like CSV.
* **Advanced Ingestion:** Implementing recursive lookups and handling complex JSON structures.
* **Performance Optimization:** Reducing job overhead by moving from `inferSchema` to manual schema definitions.
* **Data Quality:** Mastering "bad record" handling and nested data transformation.

---

<div id="columnar-formats"></div>

## 1. Why Columnar Data Formats are Useful

Columnar formats (like Parquet and ORC) store data by column rather than by row, which is revolutionary for Big Data for several reasons:

* **Column Pruning:** Spark only reads the specific columns required for a query. If you have a table with 100 columns but only `select` two, Spark skips the rest of the data on disk, drastically reducing I/O.
* **Superior Compression:** Because data in a single column is of the same type (e.g., all integers), compression algorithms like Snappy or Zstd work much more efficiently than they do on mixed-type rows.
* **Predicate Pushdown:** These formats store metadata (min/max values) for data blocks. This allows Spark to "skip" entire files that don't match a filter (e.g., `WHERE age > 25`) without actually reading the content.

---

<div id="parquet-read"></div>

## 2. How to Read a Parquet File in PySpark

Parquet is the default format for Spark. It is self-describing, meaning the schema is embedded within the file metadata.

**Example:**

```python
# Reading using the generic format method
df = spark.read.format("parquet").load("path/to/data.parquet")

# Using the shortcut method
df = spark.read.parquet("path/to/data.parquet")

```

---

<div id="orc-details"></div>

## 3. Working with ORC (Optimized Row Columnar)

ORC is a highly efficient columnar format originally created for Apache Hive.

* **ORC Details:** It is designed to reduce the size of the original data by up to **75%**. It supports ACID properties and provides a "Stripe" structure which contains index data, row data, and a stripe footer, making it incredibly fast for heavy analytical queries.
* **How to read:**

```python
df = spark.read.format("orc").load("path/to/data.orc")

```

---

<div id="recursive-lookup"></div>

## 4. Recursive File Read (recursiveFileLookup)

By default, Spark only looks for files in the specific directory you provide. If your data is nested in multiple sub-directories (e.g., `year/month/day/`), Spark will ignore them.

To achieve a recursive read, you must set the `recursiveFileLookup` option to `true`. This forces Spark to traverse the entire folder tree.

**Example:**

```python
df = (spark.read.format("parquet")
      .option("recursiveFileLookup", "true")
      .load("path/to/parent_folder/"))

```

---

<div id="json-handling"></div>

## 5. Handling JSON Data: Single-line vs. Multi-line

The way Spark reads JSON depends entirely on the file's structure:

* **Single-line JSON (Standard):** Spark expects one valid JSON object per line. This is the fastest way to process JSON as it allows Spark to split files across different executors easily.
* **Multi-line JSON:** If a single JSON object is "pretty-printed" and spans multiple lines (using newlines and indentation), Spark will fail to parse it correctly unless you set `.option("multiLine", "true")`. Note that this can impact performance as the file becomes harder to split.

---

<div id="from-json"></div>

## 6. The `from_json` Function and Real-World Applications

The `from_json` function is used to transform a string column containing JSON into a structured Spark `StructType` or `MapType`.

* **Real-World Application:** This is essential when consuming data from **Kafka** or other message brokers. Usually, the "Value" of a Kafka message is just a raw string; `from_json` allows you to parse that string into real, queryable columns based on a predefined schema.

---

<div id="to-json"></div>

## 7. The `to_json` Function

`to_json` is the inverse of `from_json`. It takes multiple columns or a Struct and collapses them into a single JSON string column.

* **Real-World Application:** This is frequently used when preparing data to be sent to a **Web API** or a **NoSQL database** (like MongoDB) that requires a specific JSON payload format.

---

<div id="nested-data"></div>

## 8. Explode and Selecting Elements within a Struct

Working with nested data requires specialized functions:

* **`explode()`:** If a column contains an **Array**, `explode` will create a new row for every single element in that array, effectively "flattening" the list.
* **Selecting Struct Fields:** You can access nested data within a `StructField` using simple **dot notation**.

**Example:**

```python
from pyspark.sql.functions import explode

# Explode an array into individual rows
df_exploded = df.withColumn("item", explode(df.orders_array))

# Select specific fields from within the struct
df_final = df_exploded.select("customer_id", "item.product_name", "item.price")

```

---

<div id="spark-internals"></div>

## 🛠 Spark Internals: The "Hidden Cost" of Reading Data

I analyzed the **Spark UI (port 4040)** to understand how simple read commands impact performance:

* **Metadata Discovery:** Even though reading data is a *transformation*, Spark often triggers a job to identify metadata.
* **The Problem with `inferSchema`:** Enabling `inferSchema: true` triggers **two jobs**—one to read the header and another to scan the dataset to guess types.
* **The Solution:** By defining a **manual schema** using `.schema(my_schema)`, I eliminated these extra jobs, allowing Spark to skip the scanning phase and optimize the execution plan immediately.

---

<div id="bad-records"></div>

## ⚠️ Handling Bad Records (Read Modes)

Data quality varies. I implemented and compared three primary modes to handle malformed data:

| Mode | Behavior | Best Use Case |
| --- | --- | --- |
| **Permissive** (Default) | Sets mismatched columns to `null` and captures the raw error in a `_corrupt_record` column. | Debugging and data auditing. |
| **DropMalformed** | Silently drops any row that contains data not matching the schema. | When you only require clean data for downstream analysis. |
| **FailFast** | Throws an exception and stops the job the moment an error is encountered. | Critical pipelines where data loss is unacceptable. |

---

<div id="best-practices"></div>

## 💡 Best Practices Implemented

* **Manual Schema Definition:** Improves performance and ensures data integrity.
* **Clean Code Patterns:** Instead of chaining multiple `.option()` calls, I utilized **Python dictionary unpacking** (`.options(**config_dict)`) to keep the codebase modular.

```python
_options = {
    "recursiveFileLookup" : "true",
    "multiLine" : "true"
}

df = (spark.read.format("json")
      .options(**_options)
      .load("data/input/"))
```