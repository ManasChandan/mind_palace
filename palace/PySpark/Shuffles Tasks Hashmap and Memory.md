# 🚀 Deep Dive: Spark Internals, Shuffles, and Memory

This guide explains how Apache Spark operates "under the hood," specifically focusing on the transition from Narrow to Wide transformations, Shuffle mechanics, and Executor-level task execution.

## 1. The Logical Pipeline

When executing a query like:
`Filter (Salary > 10k) -> GroupBy (Dept_ID, Avg) -> Join (Dept_Names)`

Spark divides the work into **Stages** separated by **Shuffle Boundaries**.

### Stage 1: The Map Side (Narrow Operations)

* **Pipelining:** Narrow operations (Filter, Map) are combined into a single "Whole-Stage Code Gen" task. Spark reads data and applies the filter in-memory without writing to disk.
* **Map-Side Partial Aggregate:** Instead of shuffling every raw row, Spark uses an internal **Hash Map** to store partial results (e.g., `Dept_10 -> [Sum: 50k, Count: 2]`). This significantly reduces network traffic.

### The Shuffle Boundary

This is a physical "fence." Stage 1 must write its data to local disk before Stage 2 can begin.

* **Partitioning:** For every row, Spark calculates a **Partition ID** using .
* **The Data File:** A single file containing all data sorted by destination Partition ID.
* **The Index File:** A small file storing byte offsets, telling Reducers exactly where their specific partition starts and ends within the Data File.

---

## 2. The Shuffle Mechanism (The "Pull" Model)

Spark uses a **Pull Model**, meaning data is never "pushed" to the next stage; it is requested.

1. **The Request:** Reducer Task #9 (responsible for Partition 9) asks the **Driver** where its data lives.
2. **The Fetch:** Task 9 initiates a **Shuffle Read**, reaching out to the "Shuffle Service" on all Executors to pull only the byte ranges associated with Partition 9.
3. **The Transfer:** Data is moved over the network (or local disk if on the same node).

---

## 3. Executor & Task Architecture

Consider a setup with **2 Executors**, each having **4 Cores** (8 slots total).

| Component | Responsibility |
| --- | --- |
| **Slots (8)** | Determine how many partitions can be processed in parallel. |
| **Task** | The unit of execution. 1 Task = 1 Partition + 1 CPU Core. |
| **Executor RAM** | Divided into **Storage Memory** (Caching) and **Execution Memory** (Shuffle/Join/Agg). |
| **Tungsten** | Spark's engine that manages data in "Unsafe" raw binary format to avoid Java Garbage Collection (GC) overhead. |

---

## 4. In-Memory Operations: The Hash Map

The **Hash Map** is the engine of the GroupBy and Join operations.

* **Mechanism:** Spark uses a `BytesToBytesMap`. It hashes the `Dept_ID` to find a memory address and updates the values (Sum/Count) in-place.
* **The Join:** In a **Sort-Merge Join**, Spark shuffles both tables by the Join Key (`Dept_ID`). The Reducer pulls both sides, sorts them (using pointers), and "zips" them together.
* **Spilling:** If a Hash Map grows larger than the allocated **Execution Memory**, Spark "spills" it to disk. This triggers heavy Disk I/O and kills performance.

---

## 5. Performance Optimization & Tuning

### The Shuffle Partition Knob

The setting `spark.sql.shuffle.partitions` (default 200) is critical:

* **Too High:** Creates many tiny tasks. The overhead of scheduling and creating small files outweighs the processing time.
* **Too Low (The 1TB Disaster):** If 1TB is split into only 16 partitions, each task handles ~64GB. This exceeds RAM, causing constant **Disk Spilling** and massive **GC Pressure**.
* **The Sweet Spot:** Aim for **128MB – 200MB per partition**.

## 📝 Summary Checklist for Debugging

1. **Check Spark UI:** Look for the "Shuffle Read" size. Is one task taking much longer than others? (Data Skew).
2. **Spill to Disk:** If you see "Spill (Memory)" and "Spill (Disk)" in the UI, increase your shuffle partitions.
3. **GC Time:** If the task bar is red, your partitions are too large or your Executor memory is too low.

# MANAS MIND MAP :)

This is my mind map which I got reviewd with gemini. 

### 1. The Filter is done for each task.

* **Correct.** This happens in Stage 1 as a **narrow** operation. Every core filters its own chunk of data in-memory.

### 2. The next step is Group By.

* **Correct.** But remember, this is where the code "splits." Spark starts a **Partial Aggregate** before any data moves.

### 3. Spark creates the Partition IDs.

* **Refinement:** Spark calculates a Partition ID **for every row** using . This determines which "bucket" the data belongs to for the shuffle.

### 4. Creates a hash map for this partition IDs.

* **Correction:** The Hash Map is actually keyed by the **Department ID**, not the Partition ID.
* The **Partition ID** is just used to decide which file/bucket to put the result in. The **Hash Map** is used to do the math (the Sum/Count) for each specific Department.

### 5. The key is Partition ID and the value is Sum and Count.

* **Correction:** The key is the **Dept_ID**.
* *Example:* If Partition #5 contains "Dept A" and "Dept B", the Hash Map inside that task looks like:
* `Dept A -> [Sum: 100, Count: 1]`
* `Dept B -> [Sum: 200, Count: 2]`


* Both of these belong to **Partition 5**.

### 6. Executor writes this and sends Index File for this hash table.

* **Refinement:** The Executor writes the **Data File** (the actual values) and the **Index File** (the map of where each Partition ID starts in the Data File).
* It doesn't send the file yet! It just tells the **Master** it is ready.

### 7. Reducer collects all the same partition key hashes from the respective workers.

* **Correct.** The Reducer for "Partition 5" reaches out to all Executors and says: *"Give me all data you have labeled as Partition 5."* It pulls the partial Sums and Counts.

### 8. For the department, a new hash table is created... key as hash dept id and value is dept name.

* **Correct (assuming a Hash Join):** If you are doing a Join, Spark shuffles the "Department Names" table the exact same way.
* Because they used the same  formula, "Dept 10" from the Employees table and "Dept 10" from the Names table are guaranteed to end up in the same Reducer task.

### 9. Joined by getting the hash from department table and the hash post group by sum.

* **Correct:** The Reducer now has two sets of data for the same Partition:
1. The aggregated Averages (from the Employee shuffle).
2. The Department Names (from the Department shuffle).


* It performs the final match in memory.

---

### The Updated Mental Model

If I were to summarize your points into a "Final Spark Flow":

1. **Map Tasks:** Filter  Group by **Dept_ID** (Local Hash Map)  Assign **Partition_ID**  Write Data/Index Files.
2. **Shuffle:** Reducers **Pull** data based on **Partition_ID**.
3. **Reduce Tasks:** Finalize Average Math  Look up **Dept_ID** in the "Department Name" Hash Map  Output Final Joined Row.

### A Wit's Tip:

Think of the **Partition ID** as the **Zip Code** (where the mail goes) and the **Dept ID** as the **Person's Name** (who the mail is for). Spark moves mail by Zip Code, but once it arrives at the house, it uses the Name to make sure the right person gets the right letter.

# More on Hash maps

In the context of Spark, a **Hash Map** is the primary data structure used to perform aggregations and joins without having to sort the data first.

Think of it as a "Look-up Table" stored in the Executor's RAM. It maps a **Key** (e.g., `Dept_ID`) to a **Value** (e.g., `Running_Sum`).

---

## 1. How a Hash Map Works (The Basics)

A Hash Map consists of two main parts:

1. **The Hash Function:** A formula that turns a Key (like "Dept 10") into a number (like `42`).
2. **The Array (Buckets):** A physical block of memory. The number `42` tells Spark exactly which "slot" in that memory block to look at.

**The "In-Memory" Process:**

* Spark sees a row: `Dept: 10, Salary: 5000`.
* It hashes `10`  Result: `Slot 42`.
* It jumps to `Slot 42`. If it’s empty, it writes `5000`. If it's not, it adds `5000` to whatever is already there.

---

## 2. Where it fits in the Shuffle Picture

The Hash Map appears in **two distinct locations** during your `groupBy` and `join` operation.

### A. The Map-Side (Stage 1: Partial Aggregate)

Before the shuffle even happens, Spark uses a Hash Map to **shrink the data**.

* **Without a Hash Map:** If you have 1 million employees in Dept 10, you would have to shuffle 1 million rows across the network.
* **With a Hash Map:** As the Map Task reads the partition, it updates a local Hash Map. By the time the task is done, it only has **one row** for Dept 10: `(Sum: X, Count: Y)`.
* **Shuffle Impact:** You now only send 1 row over the network instead of 1 million. This is called **Map-Side Combining**.

### B. The Reduce-Side (Stage 2: Final Aggregate or Hash Join)

Once the Reducer pulls all the chunks from across the cluster, it uses a Hash Map again.

* **For GroupBy:** It merges the partial results from all Executors into one final Hash Map to get the total average.
* **For Join (Broadcast or Shuffled Hash Join):** It takes the smaller table (e.g., `Departments`) and builds a Hash Map of it in RAM. Then, it streams the `Employees` table through. For every employee, it hashes their `Dept_ID` and does a "sub-second" lookup in the map to find the Department Name.

---

## 3. The "Tungsten" Twist: BytesToBytesMap

Standard Java HashMaps (like `java.util.HashMap`) are "heavy" because they store every number as a "Boxed Object," which wastes space.

Spark uses a special version called the **BytesToBytesMap**.

* It stores everything as **raw binary**.
* Instead of storing a "Department Object," it stores a pointer to a specific byte address in the Executor's memory.
* **Why it matters:** This allows Spark to fit **5x to 10x more data** in the same amount of RAM compared to standard Java code.

---

## 4. When the Map "Fits" vs. "Spills"

This is the connection to our previous talk about partitions:

| Status | Behavior |
| --- | --- |
| **It Fits** | The Hash Map stays in the "Execution Memory" of the core. Lookups are nearly instantaneous (nanoseconds). |
| **It Fails (Collision)** | If two different IDs hash to the same slot, Spark uses "Open Addressing" to find the next empty slot nearby. |
| **It Spills** | If the number of unique `Dept_IDs` is so large that the Hash Map fills up the allocated RAM, Spark **spills the map to disk**. It freezes the map, writes it as a sorted file, and starts a new empty map. |

---

## Summary

The **Hash Map** is the "Engine" inside the Task.

* **In Stage 1:** It’s a "Aggregator" that reduces network traffic.
* **In Stage 2:** It’s a "Matcher" that completes the Join or GroupBy.

**The Shuffle is the act of moving data, but the Hash Map is the tool that organizes that data once it arrives.**

# 📊 Spark Cluster Sizing Calculator

This table assumes a **balanced workload** (mix of joins and aggregations) and a target of **5 cores per executor** for optimal HDFS/network throughput.

| Data Volume | Target Partition Size | Total Partitions | Recommended Total RAM | Total Cores | Executor Config (5 Cores/ea) |
| --- | --- | --- | --- | --- | --- |
| **100 GB** | 128 MB | ~800 | 200 - 300 GB | 40 - 80 | 8 - 16 Executors |
| **500 GB** | 128 MB | ~4,000 | 1 - 1.5 TB | 160 - 240 | 32 - 48 Executors |
| **1 TB** | 256 MB | ~4,000 | 2 - 3 TB | 300 - 500 | 60 - 100 Executors |
| **10 TB** | 256 MB | ~40,000 | 20 - 30 TB | 1,000+ | 200+ Executors |

---

### 🧠 The Logic Behind the Numbers

To explain this in an interview or to a teammate, use these four "Rules of Three":

#### 1. The RAM Multiplier (3x)

* **Formula:** `Input Data Size * 3`.
* **Why:** 1x for the raw data, 1x for the Shuffle/Execution (Tungsten buffers), and 1x for the User Objects/Overhead. If you plan to **cache** the data, add another 1x.

#### 2. The Core-to-Partition Ratio (1:3 or 1:4)

* **Formula:** `Total Partitions / Cores`.
* **Why:** You don't want 1 core to handle only 1 partition. If that partition is skewed (larger than others), your whole job waits. If a core handles 3–4 partitions in a row ("waves"), the workload averages out, and the cluster stays efficient.

#### 3. The "Magic 5" (Executor Cores)

* **Formula:** `spark.executor.cores = 5`.
* **Why:** * **1 Core:** Too much overhead per executor.
* **>5 Cores:** Excessive HDFS write contention and massive Garbage Collection (GC) pauses because the memory pool is shared by too many threads.



#### 4. The 64GB Ceiling

* **Formula:** `spark.executor.memory = < 64GB`.
* **Why:** Keeping executors under 64GB (ideally around 32GB) helps keep JVM "Compressed Oops" (Ordinary Object Pointers) active, which makes memory usage more efficient. If you need more RAM, add more executors, don't just make them bigger.

---

### 🛠️ Example Execution Plan for your Github

If you are running your **1TB** job on a cluster with **20 Executors (5 cores each = 100 cores total)**:

1. **Shuffle Partitions:** Set to `4000`.
2. **Rounds:** Each core will process 40 partitions ().
3. **Time Per Task:** If each 256MB task takes 30 seconds, your total shuffle stage will take ~20 minutes ().
4. **Scaling:** If you need it in 10 minutes, you double the executors to 40.