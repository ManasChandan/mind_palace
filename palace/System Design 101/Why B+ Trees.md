# Why Databases Rely on B+ Trees: From Naive Files to Efficient Storage

Ever wondered why almost every major database from relational SQL systems to NoSQL giants like MongoDB—chooses the **B+ tree** as its core storage structure? While it might seem like a complex academic concept, the evolution of database storage reveals that B+ trees are a practical solution to the physical limitations of disk-based storage.

### The Naive Starting Point: Sequential Files

To understand the genius of the B+ tree, we first have to look at the simplest way to store data: a single file where rows or documents are written one after another. While this "naive" implementation is easy to build, it quickly becomes a performance nightmare as your data grows:

*   **Insertions (Order N):** You cannot simply "insert" a line into the middle of a file on a disk. To maintain a specific order (like a primary key), you would have to create a brand-new file, copy everything before the insertion point, add the new row, and then copy everything after it.
*   **Updates:** If a row's width increases (e.g., updating 100 bytes of data to 120 bytes), you risk overwriting the next row’s data. Again, this often forces a full file rewrite.
*   **Searches and Deletions:** Finding a single row requires a **linear scan** (checking every row from the start), and deleting a row involves rewriting the entire file just to reclaim the empty space.

In this naive world, almost every operation is **Order N**, meaning the database gets slower and slower as more data is added.

### The B+ Tree Solution: Optimising for the Disk

The B+ tree solves these issues by breaking data into **nodes** that correspond to the way hardware actually works.

It stores all actual data records in linked leaf nodes, while internal nodes act as indexes with only keys for navigation.

#### 0. B+ Trees Implementation

<B>The Leaf Split (Data Level)</B>

When a leaf node exceeds its capacity, it must split. In a B+ Tree, the leaf nodes are special because they must keep a copy of everything.

The Logic:

- Find the middle: Cut the overcrowded leaf in half.
- Create a sibling: Move the right half of the data into a brand-new leaf node.
- Link them: Point the old leaf’s next pointer to the new leaf (creating the linked list).
- Promote (Copy): Take the first key of the new right-hand leaf and send a copy of it to the parent.

<B>The Internal Split (Roadmap Level)</B>

If the parent node becomes too full because of the promotions, it also has to split. This is slightly different because internal nodes don't store actual data—they only store "signs."

The Logic:

- Find the middle: Identify the middle key.
- Create a sibling: Move everything to the right of the middle key into a new internal node.
- Promote (Move): The middle key itself is moved up to the grandparent. It does not stay behind (unlike the leaf split).
- Re-parent: All the children that were moved to the new node must now point to that new node as their "father."

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

#### 1. Matching the Disk Block Size
Most operating systems perform disk I/O in **4KB blocks**. Even if you only want to read one byte, the system reads the entire 4KB block. B+ trees leverage this by making each tree node 4KB in size. If an average row is 40 bytes, one node can hold roughly 100 rows, allowing the database to fetch 100 rows in a single disk read.

#### 2. The Power of "Leaf" and "Internal" Nodes
Unlike a standard B-tree, a B+ tree forces all actual table data (rows/documents) into the **leaf nodes** at the bottom of the tree. The nodes above them—**internal or non-leaf nodes**—act as "routing information." They store ranges (e.g., "IDs 1 to 200 go left, IDs 201 to 400 go right") to guide the database to the correct disk offset.

### How Operations Become "Logarithmic"

By using this tree structure, the database can perform operations with incredible efficiency:

*   **Finding a Row:** To find ID #3, the database reads the root node, follows the pointer to the correct child node, and finally reads the leaf node. Instead of scanning millions of rows, it performs just **three or four discrete disk reads** to find any specific piece of data.
*   **Insertions and Updates:** Because data is stored in discrete blocks, the database only needs to find the specific 4KB node, update it in memory, and flush that single block back to disk. There is no need to rewrite the entire database file.
*   **Range Queries:** This is where the B+ tree truly shines. All leaf nodes are **linearly connected** (linked together). If you want all IDs from 100 to 600, the database finds ID 100 and then simply "walks" across the leaves until it hits 600. This makes range queries super-efficient and predictable.

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

![BEST PHOTO EXPLAINING B+ TREES AND DATA](https://media.geeksforgeeks.org/wp-content/uploads/20230623132658/ezgifcom-gif-maker-(14)-768.webp)

### Final Thoughts

The B+ tree is the backbone of modern data storage because it respects the constraints of physical disks while providing **predictable, high-speed performance**. Whether it is MySQL's InnoDB or MongoDB's WiredTiger engine, the B+ tree ensures that your "Find One" or "Range Query" stays fast, no matter how large your dataset becomes.

***

*Note: This summary is based on the insights shared by Arpit Bhayani's Youtube Channel* ([Arpits Youtube Channel](https://www.youtube.com/@AsliEngineering))