# Why Databases Rely on B+ Trees: From Naive Files to Efficient Storage

Ever wondered why almost every major database—from relational SQL systems to NoSQL giants like MongoDB—chooses the **B+ tree** as its core storage structure? While it might seem like a complex academic concept, the evolution of database storage reveals that B+ trees are a practical solution to the physical limitations of disk-based storage.

### The Naive Starting Point: Sequential Files

To understand the genius of the B+ tree, we first have to look at the simplest way to store data: a single file where rows or documents are written one after another. While this "naive" implementation is easy to build, it quickly becomes a performance nightmare as your data grows:

*   **Insertions (Order N):** You cannot simply "insert" a line into the middle of a file on a disk. To maintain a specific order (like a primary key), you would have to create a brand-new file, copy everything before the insertion point, add the new row, and then copy everything after it.
*   **Updates:** If a row's width increases (e.g., updating 100 bytes of data to 120 bytes), you risk overwriting the next row’s data. Again, this often forces a full file rewrite.
*   **Searches and Deletions:** Finding a single row requires a **linear scan** (checking every row from the start), and deleting a row involves rewriting the entire file just to reclaim the empty space.

In this naive world, almost every operation is **Order N**, meaning the database gets slower and slower as more data is added.

### The B+ Tree Solution: Optimising for the Disk

The B+ tree solves these issues by breaking data into **nodes** that correspond to the way hardware actually works.

#### 1. Matching the Disk Block Size
Most operating systems perform disk I/O in **4KB blocks**. Even if you only want to read one byte, the system reads the entire 4KB block. B+ trees leverage this by making each tree node 4KB in size. If an average row is 40 bytes, one node can hold roughly 100 rows, allowing the database to fetch 100 rows in a single disk read.

#### 2. The Power of "Leaf" and "Internal" Nodes
Unlike a standard B-tree, a B+ tree forces all actual table data (rows/documents) into the **leaf nodes** at the bottom of the tree. The nodes above them—**internal or non-leaf nodes**—act as "routing information." They store ranges (e.g., "IDs 1 to 200 go left, IDs 201 to 400 go right") to guide the database to the correct disk offset.

### How Operations Become "Logarithmic"

By using this tree structure, the database can perform operations with incredible efficiency:

*   **Finding a Row:** To find ID #3, the database reads the root node, follows the pointer to the correct child node, and finally reads the leaf node. Instead of scanning millions of rows, it performs just **three or four discrete disk reads** to find any specific piece of data.
*   **Insertions and Updates:** Because data is stored in discrete blocks, the database only needs to find the specific 4KB node, update it in memory, and flush that single block back to disk. There is no need to rewrite the entire database file.
*   **Range Queries:** This is where the B+ tree truly shines. All leaf nodes are **linearly connected** (linked together). If you want all IDs from 100 to 600, the database finds ID 100 and then simply "walks" across the leaves until it hits 600. This makes range queries super-efficient and predictable.

### Final Thoughts

The B+ tree is the backbone of modern data storage because it respects the constraints of physical disks while providing **predictable, high-speed performance**. Whether it is MySQL's InnoDB or MongoDB's WiredTiger engine, the B+ tree ensures that your "Find One" or "Range Query" stays fast, no matter how large your dataset becomes.

***

*Note: This summary is based on the insights shared by Arpit Bhayani's Youtube Channel* ([Arpits Youtube Channel](https://www.youtube.com/@AsliEngineering))