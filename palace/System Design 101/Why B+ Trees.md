# Why Databases Rely on B+ Trees: From Naive Files to Efficient Storage

Ever wondered why almost every major database from relational SQL systems to NoSQL giants like MongoDB—chooses the **B+ tree** as its core storage structure? While it might seem like a complex academic concept, the evolution of database storage reveals that B+ trees are a practical solution to the physical limitations of disk-based storage.

---

<div id="table-of-contents">
<h3>Table of Contents</h3>
<ul>
<li><a href="#naive-starting-point">The Naive Starting Point: Sequential Files</a></li>
<li><a href="#b-plus-tree-solution">The B+ Tree Solution: Optimising for the Disk</a>
<ul>
<li><a href="#implementation">B+ Trees Implementation</a></li>
<li><a href="#matching-disk-block">Matching the Disk Block Size</a></li>
<li><a href="#power-of-nodes">The Power of "Leaf" and "Internal" Nodes</a></li>
</ul>
</li>
<li><a href="#logarithmic-operations">How Operations Become "Logarithmic"</a></li>
<li><a href="#pseudocode-file-ops">Pseudocode of Actual File Operations</a></li>
<li><a href="#final-thoughts">Final Thoughts</a></li>
<li><a href="#secondary-index-and-all-file-lookup">Secondary Indexes and All File Lookups</a></li>
<li><a href="#how-delete-works">How Row Deletion Works</a></li>
<li><a href="#how-col-data-type-change">How Column Data Type Change Works</a></li>
</ul>
</div>

---

<div id="naive-starting-point"></div>

### The Naive Starting Point: Sequential Files

To understand the genius of the B+ tree, we first have to look at the simplest way to store data: a single file where rows or documents are written one after another. While this "naive" implementation is easy to build, it quickly becomes a performance nightmare as your data grows:

* **Insertions (Order N):** You cannot simply "insert" a line into the middle of a file on a disk. To maintain a specific order (like a primary key), you would have to create a brand-new file, copy everything before the insertion point, add the new row, and then copy everything after it.
* **Updates:** If a row's width increases (e.g., updating 100 bytes of data to 120 bytes), you risk overwriting the next row’s data. Again, this often forces a full file rewrite.
* **Searches and Deletions:** Finding a single row requires a **linear scan** (checking every row from the start), and deleting a row involves rewriting the entire file just to reclaim the empty space.

In this naive world, almost every operation is **Order N**, meaning the database gets slower and slower as more data is added.

<div id="b-plus-tree-solution"></div>

### The B+ Tree Solution: Optimising for the Disk

The B+ tree solves these issues by breaking data into **nodes** that correspond to the way hardware actually works.

It stores all actual data records in linked leaf nodes, while internal nodes act as indexes with only keys for navigation.

<div id="implementation"></div>

#### 0. B+ Trees Implementation

<B>The Leaf Split (Data Level)</B>

When a leaf node exceeds its capacity, it must split. In a B+ Tree, the leaf nodes are special because they must keep a copy of everything.

The Logic:

* Find the middle: Cut the overcrowded leaf in half.
* Create a sibling: Move the right half of the data into a brand-new leaf node.
* Link them: Point the old leaf’s next pointer to the new leaf (creating the linked list).
* Promote (Copy): Take the first key of the new right-hand leaf and send a copy of it to the parent.

<B>The Internal Split (Roadmap Level)</B>

If the parent node becomes too full because of the promotions, it also has to split. This is slightly different because internal nodes don't store actual data—they only store "signs."

The Logic:

* Find the middle: Identify the middle key.
* Create a sibling: Move everything to the right of the middle key into a new internal node.
* Promote (Move): The middle key itself is moved up to the grandparent. It does not stay behind (unlike the leaf split).
* Re-parent: All the children that were moved to the new node must now point to that new node as their "father."

```
FUNCTION Insert(key, value):
    1. Find the correct Leaf for this key.
    2. Add (key, value) to Leaf in sorted order.
    
    3. IF Leaf is full (size == Order):
        SplitLeaf(Leaf)

FUNCTION SplitLeaf(Leaf):
    1. NewLeaf = Create new empty node
    2. Move second half of Leaf's keys/values to NewLeaf
    3. NewLeaf.next = Leaf.next
    4. Leaf.next = NewLeaf
    
    5. PromotionKey = NewLeaf.keys[0]  (The smallest value in the new side)
    6. InsertIntoParent(Leaf, PromotionKey, NewLeaf)

FUNCTION InsertIntoParent(LeftChild, Key, RightChild):
    1. IF LeftChild is Root:
        Create NewRoot
        NewRoot.keys = [Key]
        NewRoot.children = [LeftChild, RightChild]
        STOP
        
    2. Parent = LeftChild.parent
    3. Add Key and RightChild to Parent in sorted order
    
    4. IF Parent is full:
        SplitInternal(Parent)

FUNCTION SplitInternal(Node):
    1. NewNode = Create new empty node
    2. MiddleKey = Node.keys[middle_index]
    
    3. Move keys/children AFTER MiddleKey to NewNode
    4. Remove MiddleKey from the original Node
    
    5. InsertIntoParent(Node, MiddleKey, NewNode)
```

<div id="matching-disk-block"></div>

#### 1. Matching the Disk Block Size

Most operating systems perform disk I/O in **4KB blocks**. Even if you only want to read one byte, the system reads the entire 4KB block. B+ trees leverage this by making each tree node 4KB in size. If an average row is 40 bytes, one node can hold roughly 100 rows, allowing the database to fetch 100 rows in a single disk read.

<div id="power-of-nodes"></div>

#### 2. The Power of "Leaf" and "Internal" Nodes

Unlike a standard B-tree, a B+ tree forces all actual table data (rows/documents) into the **leaf nodes** at the bottom of the tree. The nodes above them—**internal or non-leaf nodes**—act as "routing information." They store ranges (e.g., "IDs 1 to 200 go left, IDs 201 to 400 go right") to guide the database to the correct disk offset.

<div id="logarithmic-operations"></div>

### How Operations Become "Logarithmic"

By using this tree structure, the database can perform operations with incredible efficiency:

* **Finding a Row:** To find ID #3, the database reads the root node, follows the pointer to the correct child node, and finally reads the leaf node. Instead of scanning millions of rows, it performs just **three or four discrete disk reads** to find any specific piece of data.
* **Insertions and Updates:** Because data is stored in discrete blocks, the database only needs to find the specific 4KB node, update it in memory, and flush that single block back to disk. There is no need to rewrite the entire database file.
* **Range Queries:** This is where the B+ tree truly shines. All leaf nodes are **linearly connected** (linked together). If you want all IDs from 100 to 600, the database finds ID 100 and then simply "walks" across the leaves until it hits 600. This makes range queries super-efficient and predictable.

<div id="pseudocode-file-ops"></div>

### Pseudocode of Actual File Operations (Thanks Google Gemini)

```
FUNCTION OpenDatabase(filename):
    IF file exists:
        Metadata = ReadPage(0)
        RootPageID = Metadata.RootID
        TotalPages = Metadata.PageCount
    ELSE:
        Create file
        RootPageID = CreateNewPage(is_leaf=True)
        SaveMetadata(RootPageID, TotalPages=1)
```

```
FUNCTION Search(TargetKey):
    CurrentID = RootPageID
    
    WHILE CurrentID is not a Leaf:
        PageData = DiskManager.ReadPage(CurrentID)
        # Find which child page to visit next
        NextID = FindChildInPage(PageData, TargetKey)
        CurrentID = NextID
        
    # We are now at the leaf page
    LeafPage = DiskManager.ReadPage(CurrentID)
    Return FindKeyInLeaf(LeafPage, TargetKey)
```

```
FUNCTION Insert(Key, Value):
    1. Search to find the LeafPageID where Key belongs.
    2. PageData = DiskManager.ReadPage(LeafPageID)
    3. Add Key/Value to PageData (in-memory).

    4. IF PageData is NOT full:
        DiskManager.WritePage(LeafPageID, PageData)
    ELSE:
        SplitFileNode(LeafPageID, PageData)

FUNCTION SplitFileNode(OldPageID, OldPageData):
    1. NewPageID = TotalPages + 1  (Get a fresh slot at the end of the file)
    2. NewPageData = Create empty page
    
    3. Partition OldPageData:
       - Keep half in OldPageData
       - Move half to NewPageData
    
    4. DiskManager.WritePage(OldPageID, OldPageData)
    5. DiskManager.WritePage(NewPageID, NewPageData)
    
    6. Promote key to Parent (using PageIDs instead of pointers)
    7. Update Metadata (TotalPages += 1)
```

<div id="secondary-index-and-all-file-lookup"></div>

### Secondary Indexes and All File lookup


#### 1. All File lookup(The "Slow" Way)

When you run a query like `SELECT * FROM users WHERE email = 'alex@example.com'` and `email` is not indexed, the database cannot use the B+ Tree "roadmap."

Instead, it performs a **Full Table Scan**.

1. **Start at the Beginning:** The database goes to the very first **Leaf Node** (the first page of the linked list at the bottom of the tree).
2. **Linear Traversal:** It reads every single record on that page, checking if the email matches.
3. **Follow the Links:** Once it finishes the first page, it uses the `next_node` pointer to jump to the second page.
4. **Repeat until the end:** It must visit **every single leaf page** in the entire database because the data is sorted by PK, not by email.

> **Performance Hit:** If you have 1 million rows, the database must load all 1 million rows into RAM just to find one email. This is  complexity.

---

#### 2. Searching with a Secondary Index (The "Double Jump")

To fix the slow scan, you create a **Secondary Index** on the `email` column. This creates a **second, completely separate B+ Tree**.

1. **Search the Secondary Tree:** The database traverses the `email` B+ Tree. The "keys (internal nodes)" in this tree are the email strings, and the "values (leaf nodes)" are the **Primary Keys** (e.g., UserID).
2. **Find the PK:** It finds `'alex@example.com'` in the leaf of the secondary tree and sees that the associated PK is `502`.
3. **Search the Primary Tree:** Now, it takes that `502` and performs a standard, lightning-fast search in the **Main B+ Tree** to get the actual row data (name, address, etc.).

> **Performance:** This is  for the first tree +  for the second tree. Even for millions of rows, this takes only a few dozen disk reads.

<div id="how-delete-works"></div>

### How Row Deletion Works

Deleting a row is actually more of a "logical" process than a physical one at first. Databases try to avoid moving data around immediately because it's expensive.

**Step A: The Primary Tree (Clustered Index)**

1. **Search:** The DB finds the leaf page containing the Primary Key (e.g., `ID: 502`).
2. **Mark for Deletion:** Instead of shifting all other records to fill the gap, the DB marks that record with a **"Delete Bit"** (often called a Tombstone).
3. **Space Reclaim:** The space is now "Free," meaning the next time you insert a record that fits in that spot, the DB will overwrite the old data.
4. **Merge (Optional):** If a page becomes too empty (e.g., more than 50% empty), the DB might merge it with a neighboring page to keep the tree compact.

*Step B: The Secondary Trees*

This is the "heavy lifting" part.

1. **Lookup:** For **every** index on that table (Email, Username, Date), the DB must go into those specific B+ Trees.
2. **Remove Entry:** It must find the leaf entry (e.g., `alex@example.com` -> `502`) and delete it.
3. **Why?** If it didn't do this, the index would point to a PK that no longer exists (a "dangling pointer"), causing errors during searches.

---

<div id="how-col-data-type-change"></div>

### How Column Data Type Change Works

Changing a data type is essentially **destroying and rebuilding** the B+ Trees. As we discussed, B+ Trees rely on the **size** and **sort order** of the data.

If you change a type that changes the size of the data, the DB usually follows these steps:

1. **The New Structure:** The DB creates a new, empty B+ Tree (Table_New) with the new data type.
2. **The Scan & Convert:** It performs a **Full Table Scan** of the old tree.
* It reads a row (e.g., `ID: 1, Age: 25`).
* It converts `25` (Integer) to `25` (BigInt).
* It inserts the converted row into the **New B+ Tree**.

3. **Index Rebuild:** Because the new rows are a different size, the "offsets" and "pointers" change. Every secondary index must be totally rebuilt from scratch to point to the new Primary Tree.
4. **The Swap:** Once the new tree is ready, the DB swaps the files and deletes the old B+ Tree.


<div id="final-thoughts"></div>

![BEST PHOTO EXPLAINING B+ TREES AND DATA](https://media.geeksforgeeks.org/wp-content/uploads/20230623132658/ezgifcom-gif-maker-(14)-768.webp)

### Final Thoughts

The B+ tree is the backbone of modern data storage because it respects the constraints of physical disks while providing **predictable, high-speed performance**. Whether it is MySQL's InnoDB or MongoDB's WiredTiger engine, the B+ tree ensures that your "Find One" or "Range Query" stays fast, no matter how large your dataset becomes.

*Note: This summary is based on the insights shared by Arpit Bhayani's Youtube Channel* ([Arpits Youtube Channel](https://www.youtube.com/@AsliEngineering))