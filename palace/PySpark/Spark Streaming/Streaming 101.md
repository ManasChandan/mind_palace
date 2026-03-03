# Deep Dive: Scalable E-Commerce Ingestion with Spark Streaming

This guide explores the high-level architecture and low-level mechanics of merging multi-source data streams.

## 1. The Code: Production-Ready Ingestion

```python
from pyspark.sql.functions import col, lit, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType

# 1. The Schema: Enforcing Data Integrity
sales_schema = StructType([
    StructField("transaction_id", StringType(), True),
    StructField("event_time", TimestampType(), True),
    StructField("item_id", StringType(), True),
    StructField("amount", DoubleType(), True)
])

# 2. Advanced Spark Configurations for State Management
# RocksDB prevents Java 'Stop-the-World' GC pauses by moving state to SSD
spark.conf.set("spark.sql.streaming.stateStore.providerClass", 
               "org.apache.spark.sql.execution.streaming.state.RocksDBStateStoreProvider")
# Optimization: Ensures shuffle partitions match your cluster's processing power
spark.conf.set("spark.sql.shuffle.partitions", "auto")

# 3. Stream Definition (The Blueprint)
def load_source(path, tag):
    return (spark.readStream
            .format("cloudFiles") # Auto Loader: Efficiently tracks new files
            .option("cloudFiles.format", "json")
            .schema(sales_schema)
            .load(path)
            .withColumn("ingestion_source", lit(tag))
            .withColumn("processed_at", current_timestamp()))

# Ingesting from 3 different business units
sources = [
    load_source("/data/web_sales/", "Web_Store"),
    load_source("/data/app_sales/", "Mobile_App"),
    load_source("/data/pos_sales/", "Physical_POS")
]

# 4. The Unified Transformation logic
# We use a 10-minute Watermark to define the 'window of trust'
deduplicated_sales = (reduce(lambda x, y: x.union(y), sources)
    .withWatermark("event_time", "10 minutes")
    .dropDuplicates(["transaction_id", "event_time"]))

# 5. The Sink: Executing the Query
query = (deduplicated_sales.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "/checkpoints/sales_pipeline")
    .trigger(processingTime='5 minutes') # The Metronome
    .toTable("gold_sales_consolidated"))

```

---

## 2. The Internal Mental Model: How it *Actually* Runs

When you click "Run," the following distributed dance occurs between the **Driver**, the **Worker**, and the **Executor**.

### Phase 1: The Driver (The Orchestrator)

* **Logical Planning:** The Driver takes your `union` and `dropDuplicates` and converts them into a **Physical Plan**. It realizes that to find duplicates, all records with the same `transaction_id` **must** meet on the same executor.
* **Offset Management:** Every 5 minutes, the Driver looks at the JSON folders. It creates a **Micro-Batch** containing only the new file paths.
* **Watermark Calculation:** The Driver calculates the "Waterline."
* *Example:* If the latest sale seen was at **12:20 PM**, and the watermark is 10 mins, the Driver tells the Executors: *"Discard anything older than 12:10 PM."*

### Phase 2: The Worker (The Physical Infrastructure)

* **The State Store (RocksDB):** Unlike a batch job, which is "forgetful," this worker has a **memory**. On its local SSD, it maintains a RocksDB database. This is a high-speed Hash Map containing every `transaction_id` that has passed through in the last 10 minutes.

### Phase 3: The Executor (The Computational Muscle)

This is where the heavy lifting happens in four distinct steps:

1. **Read & Map:** The Executor reads its assigned JSON files and converts them into rows.
2. **The Shuffle (Data Exchange):** Spark hashes the `transaction_id`. If `Transaction_A` was in a Web file and a Mobile file, the Hash ensures both copies are sent to **Executor #4**.
3. **The State Probe:** Executor #4 looks at its local RocksDB:
* *If the ID is found:* It's a duplicate. Spark drops the row immediately.
* *If the ID is NOT found:* It's a new sale. Spark writes the ID to RocksDB and passes the row to the Sink.

4. **The Eviction (Cleanup):** Once a row's `event_time` becomes older than the 10-minute watermark, the Executor **deletes** that ID from RocksDB to free up space.

---

## 3. Why this Architecture is "Senior Grade"

### 1. Lazy Evaluation & The Trigger

The trigger is on the **Write** because of Spark's lazy nature. The `writeStream` is the **Action**. Until you specify the sink, Spark doesn't know how to optimize the reads. By putting the trigger at the end, Spark can "back-propagate" the timing to all three sources simultaneously.

### 2. Idempotency and Fault Tolerance

If the cluster crashes at minute 4:59, the **Checkpoint** ensures that upon restart, Spark knows exactly which JSON files were partially processed. Because Delta Lake is **ACID compliant**, it will roll back the partial write and re-run the 5-minute batch, ensuring no sale is ever counted twice in your final table.

### 3. The "Temporal Firewall"

By using `withWatermark` + `dropDuplicates`, you aren't just cleaning data; you are creating a security layer. If a faulty system or a malicious actor tries to inject a "sale" from 3 hours ago, the watermark threshold will reject it before it ever touches your database.

## More on watermark

### 1. The Watermark Tabular Example

The Watermark is calculated at the **end** of Batch $N$ and enforced during the **start** of Batch $N+1$.

**Scenario:** * **Watermark Threshold:** 10 Minutes.

* **Initial Watermark:** 0.

| Batch | Max Event Time in **This** Batch | Calculated Watermark (Max - 10m) | Watermark Enforced in This Batch | Result for This Batch |
| --- | --- | --- | --- | --- |
| **1** | 12:10 PM | 12:00 PM | 0 (Initial) | All data accepted. |
| **2** | 12:15 PM | **12:05 PM** | **12:00 PM** (from Batch 1) | Data < 12:00 is dropped. 12:02 is **SAFE**. |
| **3** | 12:08 PM | 12:05 PM (Max seen stays 12:15) | **12:05 PM** (from Batch 2) | Data < 12:05 is dropped. 12:02 is **DROPPED**. |
| **4** | 12:25 PM | **12:15 PM** | **12:05 PM** (from Batch 3) | Data < 12:05 is dropped. |

**Key Takeaway:** In Batch 2, even though the max time was 12:15, the "drop zone" was still 12:00. This **one-batch lag** is Spark's way of ensuring that if different executors finish at slightly different times, they are all using a consistent "Global Watermark" for the entire micro-batch.

### 2. State in the Context of Aggregates

When you do a `groupBy().count()` or `sum()`, Spark creates an internal **State Table**. Without a watermark, this table grows until your cluster crashes.

#### How it works with a Watermark:

Imagine you are counting sales in **1-hour windows**.

1. **Window Creation:** A sale at 12:05 PM creates a row in the State Store for the `[12:00 - 13:00]` window.
2. **Updating State:** Every new sale at 12:30 PM, 12:45 PM, etc., updates the `count` for that 12:00-13:00 row in RAM.
3. **Watermark Guard:** The watermark tells Spark when it is **safe to delete** that row from RAM.
* If your watermark is 10 mins, Spark waits until the **Max Event Time seen reaches 13:10 PM**.
* At that moment, Spark knows that based on your rules, no more data for the `12:00 - 13:00` window will ever be accepted.

4. **Cleanup (The Eviction):** Spark clears the `12:00 - 13:00` row from the State Store.

### 3. State vs. Output Modes

How the "State" is handled depends heavily on your `outputMode`:

* **Update Mode (The "Live" View):**
* Every time the count for the `12:00 - 13:00` window changes, it is written to the sink.
* The Watermark's only job is **Cleanup**. It deletes the window from RAM after 13:10 PM so the State Store doesn't overflow.

* **Append Mode (The "Finalized" View):**
* Spark will **not** write anything for the `12:00 - 13:00` window until the Watermark hits 13:10 PM.
* It waits to make sure the result is "final" before letting you see it. This is why Append Mode feels "slow"—it's actually just being cautious.

### Summary Mental Model

* **Checkpoint:** Your "Save Game" file (Tracks where you are in the source files).
* **State Store:** Your "Active Memory" (Holds the current running totals for your windows).
* **Watermark:** Your "Garbage Collector" (Decides when a piece of memory is so old it's no longer useful).