# What is Unity Catalog ? 

In Databricks, **Unity Catalog (UC)** is the unified governance layer for data, analytics, and AI. Before Unity Catalog, data management was often fragmented across different workspaces; UC centralizes everything in one place.

To understand how it works, it is best to view it as a clear, four-level hierarchy.

---

## 1. The Hierarchy (The 3-Level Namespace)

Unity Catalog uses a "3-level namespace" to organize data. This allows you to reference data using the format `catalog.schema.table`.

1. **Metastore (The Container):** This is the top-level container that lives at the account level (not the workspace level). It stores all the metadata and permissions.
2. **Catalog (The Project/Dept):** The first layer of grouping. You might have a catalog named `sales`, `finance`, or `dev`.
3. **Schema (The Database):** Previously called "Databases," schemas live inside catalogs. They group related tables, views, and volumes (e.g., `raw_data`, `cleaned_data`).
4. **Tables / Volumes (The Assets):** The actual data objects you interact with.

## 2. Tables vs. Volumes: Where the Data Lives

In Unity Catalog, you deal with two primary types of data structures:

### **Tables (Structured Data)**

Tables are for structured data that you query using SQL or PySpark DataFrames.

* **Managed Tables:** Databricks manages the underlying files. If you drop the table, the data is deleted. These are stored in a central "Managed Storage" location.
* **External Tables:** You manage the files in your own S3/ADLS bucket. If you drop the table, the metadata is gone, but the files remain.

### **Volumes (Unstructured/Non-Tabular Data)**

Volumes are a unique Unity Catalog feature designed to handle **files that aren't tables**.

* **Use Case:** Think of images, PDFs, CSVs you want to parse manually, ML model weights, or JAR files.
* **Managed Volumes:** Managed by Databricks in the schema's default storage.
* **External Volumes:** Point to an existing cloud storage location (like a folder in an S3 bucket).
* **Access:** You can access them via a standard file path: `/Volumes/catalog/schema/volume_name/`.

## 3. How They Fit Together (The Mental Model)

Think of it like a **Digital Library**:

* **Metastore:** The entire Library System.
* **Catalog:** A specific Floor (e.g., "The Science Floor").
* **Schema:** A specific Bookshelf (e.g., "Biology").
* **Tables:** The Books (structured information you can read page by page).
* **Volumes:** The Storage Boxes at the bottom of the shelf containing loose photos and maps (unstructured files).

| Feature | Tables | Volumes |
| --- | --- | --- |
| **Format** | Delta, Parquet, CSV (mapped to rows/cols) | Any file type (PDF, PNG, TXT, etc.) |
| **Primary Tool** | SQL, Spark DataFrames | Python `os` library, Shell commands, Spark |
| **Governance** | Row/Column level security | File-level security |

## 4. Why this matters for your Code

In your PySpark script, you no longer just say `spark.table("my_table")`. You use the full path:

```python
# Reading a table in Unity Catalog
df = spark.read.table("prod_catalog.gold_schema.user_sales")

# Accessing a file in a Volume
with open("/Volumes/prod_catalog/gold_schema/raw_files/config.json", "r") as f:
    data = f.read()

```

# How to set Schemas and Volumes in databricks YML

To define Unity Catalog resources (like **Schemas** and **Volumes**) directly in your Databricks Asset Bundle, you add them to the `resources` section of your `databricks.yml`.

This is powerful because it allows you to automate the creation of your data architecture alongside your compute jobs.

### 1. Updated `databricks.yml` with Resources

Here is how you define a Schema and a Volume so they are created automatically when you run `databricks bundle deploy`.

```yaml
bundle:
  name: analytics_project

# Defining the variables to make the bundle reusable
variables:
  catalog_name:
    description: The name of the UC catalog
    default: main

targets:
  dev:
    default: true
    mode: development
    workspace:
      host: https://adb-xxxx.xx.azuredatabricks.net
      root_path: /Users/${workspace.current_user.userName}/.bundle/${bundle.name}/${bundle.target}

resources:
  # 1. Define a Schema (Database)
  schemas:
    my_analytics_schema:
      name: ${bundle.target}_schema
      catalog_name: ${var.catalog_name}
      comment: "This schema holds processed analytics data"

  # 2. Define a Volume (for raw files/unstructured data)
  volumes:
    raw_data_volume:
      name: raw_uploads
      catalog_name: ${var.catalog_name}
      schema_name: ${resources.schemas.my_analytics_schema.name}
      volume_type: MANAGED
      comment: "Landing zone for raw CSV and JSON files"

```

### 2. How this maps to your PySpark Code

Once you deploy this bundle, the volume will exist in a predictable location. You can reference it in your PySpark script using the **FUSE path** (which looks like a standard Linux file path).

**Example Pyspark Code:**

```python
# The path follows the pattern: /Volumes/<catalog>/<schema>/<volume_name>/
volume_path = f"/Volumes/main/dev_schema/raw_uploads/"

# Reading a file directly from the volume defined in your YAML
df = spark.read.format("csv").load(f"{volume_path}input_data.csv")

# Writing the processed data back to the schema defined in your YAML
df.write.mode("overwrite").saveAsTable("main.dev_schema.cleaned_table")

```

### 3. Key Tips for Managing UC via Bundles

* **Managed vs. External:** In the YAML above, I used `volume_type: MANAGED`. This is usually easier because Databricks handles the storage. If you need to point to a specific S3/ADLS folder, you would change this to `EXTERNAL` and provide a `storage_location`.
* **Permissions:** You can also add a `permissions` block to your resources in the YAML to grant `BROWSE` or `READ` access to specific groups automatically.
* **Dependency Order:** DABs are smart—they realize that the Volume depends on the Schema, so they will always create the Schema first.

When you run `databricks bundle deploy`, the Databricks CLI compares your local `databricks.yml` file to what actually exists in your workspace. If the schema and volume aren't there, **it creates them for you.**

Here is exactly what happens during that deployment process:

### 4. The Validation Phase

Before anything is built, the CLI checks your YAML. It ensures that:

* Your syntax is correct.
* You have the **permissions** to create schemas and volumes in that specific catalog.
* The names don't conflict with existing resources in a way that would cause an error.

### 5. The Dependency Tree

DABs are "state-aware." They understand that a Volume cannot exist without a Schema.

* It will first create the **Schema**.
* It will then create the **Volume** inside that schema.
* If you also defined a **Job** that reads from that volume, it waits until the volume is ready before configuring the job.

### 6. The "State" Management

This is the most important part. DABs keep track of the resources they create.

* **Update:** If you change the `comment` or a property of the volume in your YAML and redeploy, the CLI will **update** the existing volume rather than deleting and recreating it.
* **Deletion:** If you remove the volume from your `databricks.yml` and deploy, the CLI (depending on your settings) will usually leave the resource there but stop managing it, or ask if you want to destroy it.

### 7. How to verify it worked

After running `databricks bundle deploy`, you can verify the creation in two ways:

1. **In the Terminal:**
You will see output similar to:
```bash
Updating my_analytics_schema (schema)...
Updating raw_uploads (volume)...
Deployment complete!

```

2. **In the Databricks UI:**
Go to **Catalog Explorer**, find your catalog (e.g., `main`), and you should see your new schema and the volume listed inside it immediately.

### One Small Warning

While DABs create the **metadata** (the "folder" structure of the volume), they do **not** automatically upload files from your local laptop into that volume unless you explicitly tell them to using a `sync` command or a specialized artifact task.

To move files from your local computer into a Databricks Volume automatically during deployment, you use the **`sync`** directive within your bundle configuration.

This is perfect for lookup tables, configuration files, or small datasets that your PySpark script needs to run.

### 8. Update your `databricks.yml`

Add the `sync` section at the top level of your bundle definition. This tells Databricks: "Take everything in my local `data` folder and keep it mirrored in this Volume."

```yaml
bundle:
  name: analytics_project

# ... (targets and variables as before) ...

sync:
  include:
    - ./data/*.csv  # Only sync CSVs from your local data folder
    - ./config/settings.json

resources:
  schemas:
    my_schema:
      name: dev_schema
      catalog_name: main

  volumes:
    landing_zone:
      name: raw_uploads
      catalog_name: main
      schema_name: ${resources.schemas.my_schema.name}
      volume_type: MANAGED
      # This link tells the bundle WHERE to put the synced files
      remote_path: /Volumes/main/dev_schema/raw_uploads/ 

```

### 9. How the Sync Works

When you run `databricks bundle deploy`:

1. **Comparison:** The CLI looks at your local `./data` folder and the remote Volume.
2. **Upload:** It uploads any new or changed files.
3. **Clean up:** If you delete a file locally, it will (by default) delete it from the Volume to keep them perfectly in sync.

### 10. Accessing the Synced Files in PySpark

Since the files are now in a Volume, you access them using the standard Posix path. You don't need `dbutils.fs.cp` or any complex commands; you just treat it like a local file system.

```python
# The path is exactly what you defined in the 'remote_path'
local_file_in_volume = "/Volumes/main/dev_schema/raw_uploads/data/my_file.csv"

df = spark.read.csv(local_file_in_volume, header=True)
df.show()

```

### Important Considerations:

* **File Size:** Bundles are great for code and configuration (under 10MB-50MB total). If you are trying to move **Gigabytes** of data, do not use DAB sync. Instead, use the **Databricks CLI `fs cp**` command or a proper data integration tool like Azure Data Factory or AWS Glue.

* **The `.gitignore` Rule:** Make sure the files you want to sync are **not** ignored by your `.gitignore` file, otherwise the bundle might skip them.

### 11. The Multi-Volume Configuration

When you have multiple volumes, the `sync` section in your `databricks.yml` stays at the top level, but you use **specific paths** to map different local folders to different remote volumes.

Think of the `sync` block as a "routing table" that tells the bundle exactly where each local directory should land.

In this example, we have one volume for **raw data** (CSV/JSON) and another volume for **ML models** or lookup files.

```yaml
bundle:
  name: multi_volume_project

# ... targets defined here ...

resources:
  volumes:
    # Volume A: For raw data
    data_volume:
      name: raw_data
      catalog_name: main
      schema_name: my_schema
      volume_type: MANAGED

    # Volume B: For reference/lookup files
    lookup_volume:
      name: reference_files
      catalog_name: main
      schema_name: my_schema
      volume_type: MANAGED

# This is where the routing happens
sync:
  paths:
    - source: ./local_data/
      target: /Volumes/main/my_schema/raw_data/
    - source: ./local_lookups/
      target: /Volumes/main/my_schema/reference_files/

```

### 12. How it behaves during `deploy`

* **Parallel Sync:** When you run `databricks bundle deploy`, the CLI handles both paths. It ensures `./local_data/` is mirrored to the `raw_data` volume and `./local_lookups/` is mirrored to `reference_files`.
* **Isolation:** Changes in your `local_data` folder will **not** affect files in your `reference_files` volume. They are treated as completely independent sync operations.
* **Filtering:** You can still use `include` and `exclude` globally if you want to prevent certain file types (like `.DS_Store` or `.tmp` files) from being uploaded to *any* volume.

### Pro-Tip: Variable-Based Targets

If you are deploying to multiple environments (dev and prod), you should avoid hardcoding `main` or `my_schema` in the `sync` paths. Instead, use variables so the sync points to the correct volume for that specific environment:

```yaml
sync:
  paths:
    - source: ./local_data/
      # Uses the schema name defined in the resources section for the current target
      target: /Volumes/${var.catalog}/${resources.volumes.data_volume.schema_name}/${resources.volumes.data_volume.name}/

```