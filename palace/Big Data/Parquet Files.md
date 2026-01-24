## 📑 Table of Contents

* <a href="#core-philosophy">Core Philosophy: Row vs. Columnar</a>
* <a href="#physical-layout">The Physical Layout on Disk</a>
* <a href="#why-parquet-fast">Why Parquet is Faster (The Superpowers)</a>
* <a href="#performance-comparison">Performance Comparison (10M+ Rows)</a>
* <a href="#important-considerations">Important Considerations (The "Fine Print")</a>
* <a href="#ecosystem-tools">Common Ecosystem Tools</a>
* <a href="#hybrid-architecture">The "Hybrid" Architecture (Row Groups + Columns)</a>
* <a href="#schema-evolution">Schema Evolution: Handling Change</a>
* <a href="#critical-limitations">Critical Limitations & "Breaking Changes"</a>

---

<div id="parquet-guide"></div>

# 📦 Apache Parquet: The Definitive Guide

<div id="core-philosophy"></div>

## 1. Core Philosophy: Row vs. Columnar

Most traditional formats (like CSV) are **Row-oriented**. Parquet is **Column-oriented**.

* **Row-Oriented (CSV):** Data is stored as `Row1, Row2, Row3`. To find the average of one column, the computer must scan every single piece of data in every row.
* **Column-Oriented (Parquet):** Data is stored as `Column1, Column2, Column3`. The computer can jump directly to the specific column it needs, ignoring the rest.

---

<div id="physical-layout"></div>

## 2. The Physical Layout on Disk

Parquet files are structured hierarchically to allow for massive parallel processing and efficient "jumps."

### The Hierarchy:

1. **Row Groups:** Large horizontal chunks of rows (usually 128MB–512MB).
2. **Column Chunks:** Within a Row Group, each column's data is stored contiguously.
3. **Pages:** The smallest unit (approx. 1MB). This is where the actual data values live, encoded and compressed.

### The "Footer" (The Brain):

Parquet writes the metadata at the **end** of the file. This allows the writer to finish the file in a single pass.

* **Magic Number:** The file ends with `PAR1`.
* **Offsets:** The footer acts as a "GPS," telling the reader exactly at which byte a column starts.
* **Stats:** It stores Min/Max values for every column in every row group.

---

<div id="why-parquet-fast"></div>

## 3. Why Parquet is Faster (The Superpowers)

### A. Column Pruning (I/O Efficiency)

If a table has 100 columns but your query only asks for 2, Parquet physically only reads **2%** of the data from the disk.

### B. Predicate Pushdown (Data Skipping)

Because the **Footer** knows the Min/Max of every block, it can skip entire chunks of data.

* *Example:* If you filter for `Price > 1000` and a block’s Max is `800`, the computer never even opens that block.

### C. Smart Encoding & Compression

* **Dictionary Encoding:** Replaces repetitive strings (like "USA", "USA") with small integers (0, 0) and a single lookup table.
* **Run-Length Encoding (RLE):** Instead of storing "Yes" 1,000 times, it stores "Yes, repeat 1,000x."
* **Type-Specific Compression:** Since a column is all the same data type (e.g., all Integers), compression algorithms work much better than they do on mixed-type CSV rows.

---

<div id="performance-comparison"></div>

## 4. Performance Comparison (10M+ Rows)

| Feature        | CSV                      | Parquet                         |
| -------------- | ------------------------ | ------------------------------- |
| **Storage**    | Large (Text-based)       | Small (Compressed Binary)       |
| **Read Speed** | Slow (Full Scan)         | Fast (Selective Scan)           |
| **Data Types** | Everything is a "String" | Native Types (Int, Float, Date) |
| **Schema**     | No Schema                | Schema is built-in              |

---

<div id="important-considerations"></div>

## 5. Important Considerations (The "Fine Print")

While Parquet is amazing, keep these "Golden Rules" in mind:

* **Write Once, Read Many (WORM):** Parquet is optimized for heavy reading. It is expensive to "update" a single row in a Parquet file because the entire file (or at least a row group) usually needs to be rewritten.
* **Not Human-Readable:** You cannot open a Parquet file in Notepad. You need a tool (like Python, Spark, or a Parquet Viewer) to see the data.
* **Schema Evolution:** Parquet supports "Schema Evolution." You can add new columns to your data over time, and older Parquet files will simply treat those new columns as `NULL` when read together.

---

<div id="ecosystem-tools"></div>

## 6. Common Ecosystem Tools

* **Processing:** Apache Spark (native format), Pandas (via `pyarrow` or `fastparquet`), Dask.
* **Query Engines:** AWS Athena, Google BigQuery, Presto, Trino.
* **Storage:** Data Lakes (S3, Azure Blob Storage, HDFS).

---

<div id="hybrid-architecture"></div>

## 7. The "Hybrid" Architecture (Row Groups + Columns)

Parquet is technically a **Hybrid** format. It uses Row Groups to make Big Data manageable.

### How it works:

1. **Vertical Slicing:** The file is split into **Row Groups** (e.g., 1 million rows each). This allows for parallel processing (multiple computers/cores working on different groups).
2. **Horizontal Storage:** Inside each Row Group, data is stored **Columnar**. All 'Salary' values for that group are written back-to-back.

### The Footer's Role in Multi-Group Files:

The Footer contains a metadata block for **every** Row Group. If you have 4 Row Groups, the Footer stores 4 distinct byte offsets for the 'Salary' column.

**Query Execution Example (`AVG(Salary)`):**

1. **Look at Footer:** Get the 4 "GPS coordinates" (byte offsets) for the Salary column.
2. **Direct Jump:** The disk jumps to those 4 spots, skipping all other columns (ID, Name, etc.).
3. **Parallel Read:** The system reads all 4 Salary chunks at once.
4. **Aggregate:** The partial results are merged into the final average.

**Why this wins:**

* **Parallelism:** You can process different row groups on different CPU cores.
* **Memory Efficiency:** You only need to load one row group's column into RAM at a time.
* **Sequential I/O:** Reading values that are physically next to each other on disk is much faster than skipping around text in a CSV.

---

<div id="schema-evolution"></div>

## 8. Schema Evolution: Handling Change

Parquet is "self-describing," meaning each file contains its own schema. This allows the dataset to grow and change over time without breaking.

### How it Works:

* **The Union Strategy:** If you have old files (Columns A, B) and new files (Columns A, B, C), modern query engines will "merge" them. They will show Column C for all rows, but for the old files, those values will simply be **NULL**.
* **Backward Compatibility:** New code can read old data because the engine fills in missing columns with `NULL`.
* **Forward Compatibility:** Old code can read new data because the reader simply ignores any columns in the footer that it doesn't recognize.

---

<div id="critical-limitations"></div>

## 9. Critical Limitations & "Breaking Changes"

While Parquet is flexible, it is not a relational database. There are things it cannot do easily:

* **Immutable (Write-Once):** You cannot easily update a single row. To "update" data, you typically have to rewrite the entire file or row group.
* **No Renaming:** If you rename a column from `Salary` to `Pay`, Parquet treats this as deleting the old column and adding a new one. All historical data under the name `Salary` will appear as `NULL`.
* **No Type Changes:** Changing a column from an **Integer** to a **String** is a breaking change. Because the binary encoding is different, the reader will fail to parse the old data.
* **Small File Problem:** Parquet is designed for large files. If you have thousands of tiny Parquet files (a few KB each), the overhead of reading all those Footers will actually make your queries **slower** than a single CSV.
