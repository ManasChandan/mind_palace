# Stages and Jobs

## Under the Hood of Apache Spark: DAGs, Explain Plans, and Shuffle Architecture

If you have been working with Apache Spark, you know that moving from writing code to understanding how that code executes is the key to mastering optimization. In this post, we dive deep into the backend of Spark’s working mechanisms. We will explore how Spark generates tasks, interprets Directed Acyclic Graphs (DAGs), manages shuffles, and why understanding the "Explain Plan" is crucial for advanced engineering.

To demonstrate these concepts, we’ll walk through a specific experiment involving DataFrames, repartitioning, and joins.

## The Experiment Setup

To see Spark’s internals clearly, we first need to strip away some of its modern auto-optimizations. For this demonstration, we disable the **Adaptive Query Engine (AQE)** and **Broadcast Join**. This forces Spark to execute a "raw" plan, making it easier to trace the specific stages and tasks.

**The Data:**
We create two DataFrames consisting of even numbers up to 200.
*   **DataFrame 1:** Step of 2.
*   **DataFrame 2:** Step of 4.
Both are initialized with a default parallelism of 8, meaning they are read into 8 partitions initially.

**The Operation:**
1.  **Repartition:** We repartition DataFrame 1 into 5 partitions and DataFrame 2 into 7 partitions.
2.  **Join:** We join these two DataFrames.
3.  **Aggregation:** We calculate the sum of the IDs.

Because Spark is lazy, no jobs are triggered during the setup or repartitioning. The job only kicks off when we call an action, such as `.show()`.

### Decoding the Task Count: The Magic Number 229

When the action is finally triggered, the Spark UI reveals that the job consists of **6 stages** and a total of **229 tasks**. At first glance, this number seems arbitrary. However, we can calculate it precisely by understanding **Pipelining** and **Shuffle Stages**.

Spark attempts to "pipeline" or pack as many transformations as possible into a single stage. A new stage is only created when Spark encounters a **Shuffle** or **Exchange**.

Here is the exact breakdown of how we arrive at 229 tasks:

1.  **Reading Data (Stages 0 & 1):** We read two DataFrames. Since the default parallelism is 8, this creates **8 tasks** for the first DataFrame and **8 tasks** for the second.
2.  **Repartitioning (Stages 2 & 3):** Repartitioning forces a shuffle (an exchange of data).
    *   DataFrame 1 converts 8 partitions to 5, requiring **5 tasks**.
    *   DataFrame 2 converts 8 partitions to 7, requiring **7 tasks**.
3.  **The Join (Stage 4):** Joining these repartitioned datasets involves another shuffle. Spark’s default shuffle partition configuration is set to 200. Therefore, the join stage creates **200 tasks**.
4.  **The Sum (Stage 5):** Finally, to compute a single sum total from those 200 partitions, Spark aggregates everything into a single partition, requiring **1 task**.

**The Math:** $8 + 8 + 5 + 7 + 200 + 1 = 229$ tasks.

### Visualizing the Flow: DAGs and Explain Plans

The **DAG (Directed Acyclic Graph)** visualization in the Spark UI confirms this flow. You can see the initial stages reading the data, followed by "Exchange" nodes where repartitioning happens. The data is written out (Shuffle Write) and then read back in (Shuffle Read) for the join.

To see this textually, we use the **Explain Plan** (`df.explain()`). This plan is read from **bottom to top**:
1.  It starts with the `Range` (reading data).
2.  It moves to `Exchange` (repartitioning).
3.  It culminates in `HashAggregate` (the sum).

The numbers listed in the Explain Plan correspond directly to the node IDs in the DAG visualization, allowing you to map your code directly to its execution path.

### The Hidden Benefit of Shuffle Write: Skipped Stages

One of the most fascinating aspects of Spark’s architecture is how it handles subsequent jobs on the same data.

If we take our processed data and perform a new operation—like a `Union`—Spark launches a new job. However, you will notice that the early stages of this new job are marked as **"Skipped"**.

**Why?**
When Spark performs a shuffle (like our previous repartition or join), it physically writes the data to disk. If a subsequent job needs that same data, Spark detects that the shuffle write already exists. Instead of re-calculating the range and re-partitioning from scratch, it performs a **Reused Exchange**, reading directly from the previously written shuffle files.

**Fault Tolerance:**
This architecture is also critical for failure recovery. If a task fails in a later stage, Spark does not need to restart the entire pipeline from the beginning (Stage 0). It only needs to restart from the point where the last shuffle data was successfully written. This makes the system resilient and efficient.

### DataFrames vs. RDDs

Finally, it is important to remember that DataFrames are essentially abstractions built on top of **RDDs (Resilient Distributed Datasets)**. While you can access the underlying RDD of any DataFrame, modern Spark development highly recommends sticking to DataFrames and Datasets. You should only revert to RDDs if you need to physically distribute data via code or require granular control over Spark Core APIs.

***

**Key Takeaway:** By understanding how tasks are calculated and how shuffles effectively "checkpoint" data, you can move beyond writing functional Spark code to writing high-performance, optimized data pipelines. Keep exploring the DAG and Explain Plans to see what’s really happening behind your code!