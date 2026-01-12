# PySpark 1

This document summarizes the key concepts of PySpark. 
Reference - Ease With Data Youtube Pyspark Playlist. 

## Table of Contents
1. [Introduction to Spark](#1-introduction-to-spark)
2. [Spark Architecture: Under the Hood](#2-spark-architecture-under-the-hood)
3. [Transformations, Actions, and Lazy Evaluation](#3-transformations-actions-and-lazy-evaluation)
4. [DataFrames and Execution Plans](#4-dataframes-and-execution-plans)

---

## 1. Introduction to Spark

**Apache Spark** is an open-source, unified computing engine designed for parallel data processing. It is currently in high demand among Data Engineers, Analysts, and Scientists.

### Key Features
*   **Speed:** Spark processes data in-memory, making it up to 10x faster than traditional Hadoop MapReduce.
*   **Polyglot:** Supports Java, Scala (which Spark is built on), Python, and R.

### The Spark Ecosystem
Spark is structured in layers:
1.  **Low-Level API:** The foundation, consisting of RDDs (Resilient Distributed Datasets) and distributed variables.
2.  **Structured API:** Built on top of low-level APIs for optimization. Includes Spark SQL, DataFrames, and Datasets.
3.  **Libraries:** High-level tools like Structured Streaming, Advanced Analytics, and Graph Query languages.

---

## 2. Spark Architecture: Under the Hood

To understand distributed computing, Spark uses a Master-Slave architecture, visualized through a "Marble Counting" analogy where an instructor (Driver) asks groups (Executors) to count marbles.

### Key Components
*   **Driver (The "Heart"):** Maintains application information, analyzes work, and distributes/schedules tasks to executors.
*   **Executor:** A JVM process running on cluster machines. Its distinct duties are to execute code and report status back to the driver.
*   **Core:** The processing unit within an executor. One core can perform one task at a time. Parallelism is achieved by having multiple cores running tasks simultaneously.

### Jobs, Stages, and Shuffles
*   **Task:** The smallest unit of work (e.g., counting a single pouch of marbles).
*   **Shuffle:** The process of moving data between executors to group it (e.g., collecting counts from all groups to get a total).
*   **Stage:** A job is divided into stages based on **Shuffles**. A shuffle acts as a boundary; a new stage cannot begin until the data movement (shuffle) is complete.

---

## 3. Transformations, Actions, and Lazy Evaluation

Before writing code, it is essential to understand how Spark handles data operations.

### Partitions
Spark breaks input data into chunks called **Partitions**. This allows multiple executors to process different chunks of data in parallel.

### Transformations
Instructions to modify data. There are two types:
*   **Narrow Transformations:** Data from one input partition contributes to only one output partition (e.g., `select`, `where`). These are fast and do not require data movement.
*   **Wide Transformations:** Data from one input partition contributes to multiple output partitions (e.g., `groupBy`). These trigger a **Shuffle**. How shuffle works, links to be attached soon [AQE,CATALYST-OPTIMIZER]

```text
+-----------------------------------------------------------+
|               1. NARROW TRANSFORMATION                    |
|             (e.g., Select, Where, Filter)                 |
+-----------------------------------------------------------+
|  [Partition A]  =====================>  [Partition A]     |
|       |                                      |            |
|  [Partition B]  =====================>  [Partition B]     |
|                                                           |
|  * Result: Fast. No data crosses the boundary.            |
+-----------------------------------------------------------+
|                                                           |
|               2. WIDE TRANSFORMATION                      |
|             (e.g., GroupBy, Distinct)                     |
+-----------------------------------------------------------+
|  [Partition A]  =========\  /==========>  [Partition A]   |
|                           \/                              |
|                           /\   <-- SHUFFLE HAPPENS HERE   |
|  [Partition B]  =========/  \==========>  [Partition B]   |
|                                                           |
|  * Result: Slower. Data moves across the cluster.         |
+-----------------------------------------------------------+
```

### Actions
Transformations build a logical plan, but **Actions** trigger the actual execution. Examples include viewing data in the console, collecting results to the driver, or writing to an output source.

### Lazy Evaluation (The Sandwich Analogy)
Spark waits until the last possible moment (when an Action is called) to execute the computation graph.
*   *Analogy:* A sandwich shop doesn't make a sandwich until the customer pays (Action). If the customer changes their bread order halfway through, waiting prevents wasted resources.
*   *Benefit:* This allows Spark to optimize the plan and manage resources efficiently.

---

## 4. DataFrames and Execution Plans

### DataFrames
The most common Structured API. They look like tables (rows and columns) and have a schema. DataFrames are **immutable**; you cannot change them, you can only transform them to create new DataFrames.

### The Execution Workflow
When code is submitted, Spark follows a rigorous planning process:

1.  **Logical Plan:**
    *   *Unresolved Plan:* Created immediately from code.
    *   *Validation:* Checked against a catalog (column/table names) to create a *Resolved Logical Plan*.
    *   *Catalyst Optimizer:* Optimizes the logic to create the *Optimized Logical Plan*.

2.  **Physical Plan:**
    *   Spark generates multiple physical plans based on the cluster configuration.
    *   **Cost Model:** These plans are evaluated for cost/efficiency.
    *   **Selection:** The best physical plan is selected and sent to the cluster for execution.

3.  **DAG (Directed Acyclic Graph):**
    *   A visualization of the execution plan where arrow marks point to the next steps in the workflow.

```
[ User Code ]
      |
      v
[ Unresolved Logical Plan ]
      |
      +---> (Catalog / Validation)
      |
      v
[ Resolved Logical Plan ]
      |
      +---> (Catalyst Optimizer)
      |
      v
[ Optimized Logical Plan ]
      |
      v
[ Physical Plans (Multiple Options) ]
      |
      +---> (Cost Model Selection)
      |
      v
[ Selected Physical Plan ]
      |
      v
[ CLUSTER EXECUTION ]
```