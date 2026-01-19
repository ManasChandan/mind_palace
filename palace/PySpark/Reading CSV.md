# Deep Dive: Reading CSV and Optimizations using Spark UI

<div id="table-of-contents"></div>

## 📑 Table of Contents
* <a href="#learning-objectives">Key Learning Objectives</a>
* <a href="#spark-internals">Spark Internals: The "Hidden Cost" of Reading Data</a>
* <a href="#bad-records">Handling Bad Records (Read Modes)</a>
* <a href="#best-practices">Best Practices Implemented</a>

---

<div id="learning-objectives"></div>

## 🚀 Key Learning Objectives
* **Spark UI Analysis:** Monitoring background jobs triggered by metadata discovery.
* **Performance Optimization:** Reducing job overhead by moving from `inferSchema` to manual schema definitions.
* **Data Quality Management:** Handling "bad records" using Spark's built-in read modes.

---

<div id="spark-internals"></div>

## 🛠 Spark Internals: The "Hidden Cost" of Reading Data
During development, I analyzed the **Spark UI (port 4040)** to understand how simple read commands impact performance.



* **Metadata Discovery:** Even though reading data is a *transformation*, Spark often triggers a job to identify metadata.
* **The Problem with `inferSchema`:** Enabling `inferSchema: true` triggers **two jobs**—one to read the header and another to scan the entire (or some) dataset to guess types.
* **The Solution:** By defining a **manual schema** using `.schema(my_schema)`, I eliminated these extra jobs, allowing Spark to skip the scanning phase and optimize the execution plan immediately.

---

<div id="bad-records"></div>

## ⚠️ Handling Bad Records (Read Modes)
Data in the wild is often messy (e.g., strings in numeric columns). I implemented and compared three primary modes to handle malformed data:

| Mode | Behavior | Best Use Case |
| :--- | :--- | :--- |
| **Permissive** (Default) | Sets mismatched columns to `null` and captures the raw error in a `_corrupt_record` column. | Debugging and data auditing. |
| **DropMalformed** | Silently drops any row that contains data not matching the schema. | When you only require clean data for downstream analysis. |
| **FailFast** | Throws an exception and stops the job the moment an error is encountered. | Critical pipelines (e.g., financial data) where data loss is unacceptable. |

---

<div id="best-practices"></div>

## 💡 Best Practices Implemented
* **Manual Schema Definition:** Improves performance and ensures data integrity.
* **Clean Code Patterns:** Instead of chaining multiple `.option()` calls, I utilized **Python dictionary unpacking** (`.options(**config_dict)`) to keep the codebase modular and readable.

```python
_options = {
    "header" : "true",
    "inferSchema" : "true",
    "mode" : "PERMISSIVE"
}

df = (spark.read.format("csv")
      .options(**_options)
      .load("data/input/emp.csv"))
```