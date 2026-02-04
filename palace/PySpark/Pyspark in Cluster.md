# Spark Cluster Architecture and Workflow
To understand how Spark works on a cluster, its described as a specific workflow involving interaction between the **Driver Program** and the **Resource Manager**:

## Workers, Executors and Cores

To understand Spark's parallel processing, it helps to think of it as a corporate hierarchy. Here is the breakdown of the relationship between **Workers**, **Executors**, and **Cores**:

### 1. The Worker Node (The Building)

A **Worker** is a physical or virtual machine within the cluster.

* It is a resource container that provides CPU, RAM, and storage to the Spark application.
* In Databricks, if you choose a cluster with 5 "Worker Nodes," you are essentially renting 5 computers to do your work.

### 2. The Executor (The Office/Department)

An **Executor** is a distributed process that runs on a Worker node.

* Its job is to run tasks and store data in memory (cache) or disk.
* A single Worker node can host one or multiple Executors depending on your configuration.
* Each Executor is dedicated to a specific Spark application; it starts when the application starts and remains until it finishes.

### 3. Cores / Slots (The Individual Workers)

A **Core** (also called a "Slot") is the smallest unit of parallel execution in Spark.

* Each core within an Executor can handle exactly **one task at a time**.
* The total number of cores across all your Executors determines your **parallelism**—the number of operations Spark can perform simultaneously.
* For example, if you have 2 Executors and each has 4 cores, you can process 8 partitions of data at the exact same moment.

### Hierarchy Summary

| Component | Responsibility | Analogous To... |
| --- | --- | --- |
| **Worker Node** | Provides the hardware/machine. | A physical office building. |
| **Executor** | Manages memory and task execution for a specific job. | A department within that building. |
| **Core** | Executes a single task/thread. | An individual employee at a desk. |

### How Databricks and Spark Use Them Together

When you write data, the **Driver** (the manager) breaks the data into partitions.

1. The **Driver** assigns a "Write Task" for each partition to an **Executor**.
2. If that **Executor** has 4 **Cores**, it can start writing 4 files (partitions) at once.
3. If there are 100 partitions to write, the cores will keep picking up new tasks until all 100 files are created on disk.

## Main Steps for Execution

*   **Resource Allocation:** When a Spark application is submitted, the **Spark Session** (the entry point) connects to the **Resource Manager** (also known as the Cluster Manager) to request specific resources, such as a set number of executors and cores.
*   **Executor Creation:** The Resource Manager communicates with the **Worker Nodes** in the cluster to allocate these resources. It creates **Executors**, which are Java Virtual Machine (JVM) processes, on the worker nodes. For example, if the request is for four executors with two cores each, the Resource Manager ensures these are spun up across the available workers.
*   **Task Execution:** Once resources are allocated, the information is sent back to the Driver Program. The Driver then copies the Python code to all executors. The Spark Session assigns specific tasks to the cores within those executors to process the data.
*   **Completion:** Executors report the status and results back to the Driver. Upon completion (success or failure), the Driver instructs the Resource Manager to shut down and deallocate the resources.

## Types of Cluster Managers

The resources identify four primary types of cluster managers responsible for allocating resources:

1.  **Standalone:** Spark’s built-in cluster manager.
2.  **YARN:** The resource manager used in Hadoop clusters.
3.  **Kubernetes:** Used for containerised environments.
4.  **Apache Mesos:** A manager that is now deprecated and no longer available.


## Deployment Modes

There are two distinct modes for deploying Spark applications, defined by where the Driver Program runs:

*   **Client Mode:** The Driver Program resides on the **client machine** (the machine submitting the job). The client is responsible for the execution lifecycle, meaning the driver is external to the cluster workers.
*   **Cluster Mode:** The Driver Program runs **inside the cluster** within an executor. The client’s only role is to submit the program; once submitted, the cluster manager handles the execution and termination, allowing the client to disconnect without stopping the job.

The primary difference between **Client mode** and **Cluster mode** lies in where the **Spark Driver** (the "brain" of your application) physically resides during execution.

### 1. Driver Location

* **Client Mode:** The Driver process runs locally on the machine where the job was submitted (e.g., your laptop or a gateway node).
* **Cluster Mode:** The Driver process is moved inside the cluster and runs on one of the worker nodes alongside the Executors.

### 2. Key Differences and Use Cases

| Feature | Client Mode | Cluster Mode |
| --- | --- | --- |
| **Driver Location** | Local machine (external to cluster). | Worker node (internal to cluster). |
| **Connectivity** | Requires a constant, stable connection between the local machine and the cluster. | The local machine can disconnect once the job is submitted. |
| **Network Traffic** | High; the Driver must constantly communicate with Executors over the network. | Low; the Driver is physically close to the Executors. |
| **Ideal For** | Interactive work, debugging, and shell-based programming (PySpark/Spark-shell). | Production pipelines and long-running batch jobs. |

### 3. Detailed Breakdown

#### **Client Mode (Interactive & Debugging)**

* **Lifecycle:** The Driver starts immediately on the local machine.
* **Feedback:** Since the Driver is local, you get immediate console output and can interact with the Spark session in real-time.
* **Risk:** If your local machine goes to sleep or loses Wi-Fi, the entire Spark job fails because the "brain" (Driver) has disappeared.

#### **Cluster Mode (Production & Stability)**

* **Lifecycle:** Your local machine sends the application code to the Cluster Manager (like YARN or Kubernetes), which then picks a worker node to start the Driver.
* **Resource Management:** The Driver consumes resources (CPU/RAM) from the cluster's pool, rather than your local computer.
* **Reliability:** Once submitted, you can close your laptop; the cluster will manage the job until completion and record logs independently.

### 4. Which one should you use?

* **Use Client Mode** when you are developing code, testing small logic snippets, or using a Jupyter Notebook.
* **Use Cluster Mode** when you are scheduling a job to run at 2 AM on a server where performance and network stability are critical.

### 5. Configuration and Execution

The resources demonstrate how to configure and monitor Spark jobs:

*   **Spark UI:** This interface allows users to monitor the status of the cluster, including the number of workers, executors, and running applications.
*   **Customising Resources:** By default, executors may launch with 1GB of memory. However, users can programmatically configure the `spark.executor.instances` (number of executors), `spark.executor.cores` (cores per executor), and `spark.executor.memory`.
*   **Parallelism:** The number of tasks running in parallel is directly dictated by the number of executor cores available. For instance, increasing the number of executors and cores allows more partitions of data to be processed simultaneously.

### 6. Production Deployment: Spark Submit

While interactive notebooks are useful for testing, the **`spark-submit`** command is the standard method for submitting jobs in a production environment.

*   **Command Structure:** The command is executed from the terminal (specifically the `bin` folder of the Spark installation). It requires defining the **Master URL** (where the cluster is running) and runtime configurations such as the number of executors, cores, and memory.
*   **Execution:** You must provide the path to the Python script (e.g., `.py` file) rather than a notebook file. This allows the job to be pushed to the cluster efficiently without an interactive session.

### 7. In Context of Databricks

In a managed environment like **Databricks**, the concepts of Client and Cluster modes are handled through the architecture of **Databricks Jobs** and **Interactive Notebooks**.

Databricks abstracts the raw `spark-submit` commands, but the underlying mechanics remain the same:

#### 1. Interactive Notebooks (Client Mode-like)

When you run code in a Databricks Notebook attached to a running cluster, it behaves similarly to **Client Mode**:

* **The Driver Location:** The Driver process runs on a specific "Driver Node" within the cluster.
* **Interaction:** The notebook UI acts as the "client" that sends commands to that Driver.
* **Lifecycle:** The Driver stays alive as long as the cluster is running, allowing you to run cells and see results immediately.

#### 2. Databricks Jobs (Cluster Mode)

When you schedule a **Databricks Job** (Workflows), the system uses **Cluster Mode** logic to ensure production-grade reliability:

* **Job Clusters:** Databricks often spins up a "Job Cluster" specifically for that task.
* **Independence:** The Driver is placed on one of the nodes within that job cluster.
* **Lifecycle:** Once the code execution finishes, the Driver shuts down, the cluster is terminated, and the results/logs are persisted in the Databricks UI. This ensures that even if you close your browser, the job continues safely in the cloud.

#### Comparison of Execution in Databricks

| Feature | Notebook Execution | Databricks Job |
| --- | --- | --- |
| **Equivalent Mode** | Client Mode | Cluster Mode |
| **Driver Residency** | Dedicated Driver Node in a persistent cluster. | A node within a temporary Job Cluster. |
| **UI Connection** | Required to send commands and view real-time output. | Not required; logs are captured and stored automatically. |
| **Purpose** | Exploration, Data Science, and Debugging. | Production ETL and scheduled pipelines. |

#### 3. Connection via Databricks Connect

For developers who want to run code from a local IDE (like VS Code or PyCharm) but use the power of a remote Databricks cluster, Databricks provides **Databricks Connect**.

* This technically uses a **Client Mode** architecture where the Spark instructions are generated on your local machine and sent to the remote Spark Driver running on the Databricks cluster.

#### How it relates to Writing Data

Regardless of the mode used in Databricks, the **Write** process follows the same distributed pattern we discussed:

* **The Driver** (on the Driver node) coordinates the commit.
* **The Executors** (on worker nodes) write the actual part-files to DBFS (Databricks File System) or S3/ADLS.
* **Success:** A `_SUCCESS` file is created at the end of the operation to signal completion.

## 8. Practcal Examples

When calculating the relationship between memory and processing power, the goal is to balance the "employees" (cores) so they don't "starve" for "desk space" (RAM).

### 1. The 4-Partition Filter Example

When you have 4 partitions of data and perform a filter operation, the hierarchy works as follows:

* **The Driver:** Receives the filter command and creates a physical plan consisting of 4 tasks (one per partition).
* **The Workers:** The Cluster Manager identifies which Worker nodes have available Executors to take on these 4 tasks.
* **The Executors:** Each task is sent to an Executor. If you have one large Executor with 4 cores, it might take all 4 tasks; if you have four small Executors with 1 core each, the tasks are distributed across them.
* **The Cores:** Each individual core picks up one partition, reads the data into the Executor's memory, applies the filter logic, and produces a filtered result in memory.
* **Parallelism:** If you have 4 cores available, all 4 partitions are filtered **simultaneously**. If you only had 2 cores, Spark would filter the first 2 partitions, finish them, and then pick up the remaining 2.

### 2. Calculating Optimal Cores per Executor

The number of cores per Executor is a critical setting (often `spark.executor.cores`). While it is tempting to give one Executor all the cores on a Worker, this often leads to performance issues.

#### **The "Rule of 5"**

A common industry best practice is to limit each Executor to **5 cores**.

* **Why?** If an Executor has too many cores (e.g., 16), they all share the same pool of memory and the same network bandwidth. This can lead to excessive **Garbage Collection (GC)** overhead, where the Java Virtual Machine (JVM) spends more time cleaning up memory than actually processing data.
* **HDFS Throughput:** When writing to HDFS, having more than 5 cores per Executor can sometimes lead to congestion in writing data.

#### **Memory per Core**

You should also calculate the **Memory per Core** to ensure your tasks don't crash with an `OutOfMemory` (OOM) error:


* **Standard Target:** Aim for **4GB to 8GB** of RAM per core for general ETL tasks.
* **Memory Intensive:** If you are doing complex joins or heavy aggregations (like bucketing or sorting), you may need **16GB+** per core.

### 3. Summary of Configuration

If you have a Worker node with **32GB RAM** and **8 Cores**, a balanced configuration might look like this:

| Configuration | Setup | Result |
| --- | --- | --- |
| **Executor Count** | 2 Executors | Better stability than 1 massive Executor. |
| **Cores per Executor** | 4 Cores | Fits the "Rule of 5" for efficiency. |
| **Memory per Executor** | 16GB | Provides 4GB per core () for the tasks. |

## What Happens for Serverless

In a **Serverless** environment (like **Databricks Serverless**), the platform completely abstracts the physical management of clusters, workers, and drivers from the user. Instead of you manually selecting a virtual machine size and waiting for it to boot, the platform maintains a "warm pool" of resources that are assigned to your code instantly.

### 1. How the Components Setup in Serverless

* **The Cluster (On-Demand Provisioning):** In serverless, there is no "fixed" cluster. The platform uses a "just-in-time" orchestration layer that logically assembles a cluster the moment you run a query.
* **The Driver (Platform-Managed):** The Driver is hosted within the cloud provider's control plane rather than your own virtual private cloud (VPC). It acts as the gateway that receives your notebook commands and handles the query planning.
* **The Workers and Executors (The Warm Pool):** The platform maintains a fleet of running worker nodes that are "pre-warmed". When you execute a job, the serverless layer carves out specific **Executors** from this pool and assigns them to your Driver.
* **Isolation:** Even though workers are shared in a warm pool, each customer's code runs in a highly secure, isolated container (like a Docker-based sandbox) to ensure data privacy.

---

### 2. The Serverless Lifecycle vs. Classic Clusters

| Feature | Classic Databricks | Databricks Serverless |
| --- | --- | --- |
| **Boot Time** | 3–7 minutes (VM setup). | Near-instant (< 10 seconds). |
| **Worker Control** | You choose VM types (e.g., `Standard_DS3_v2`). | The platform chooses the best compute for your task. |
| **Scaling** | Vertical/Horizontal scaling is manual or policy-based. | Fully automatic; it adds/removes executors as the query runs. |
| **Cost** | You pay for the cluster while it is idle. | You pay only for the seconds the compute is active. |

---

### 3. How your "4-Partition Filter" works in Serverless

When you hit "Run" on a filter operation in a serverless environment:

1. **Submission:** Your notebook sends the request to the **Serverless Driver**.
2. **Resource Allocation:** The Driver calculates that it needs enough "slots" (cores) to handle 4 partitions.
3. **Task Launch:** The platform instantly points your Driver to available **Executors** in the warm pool.
4. **Execution:** Those executors (residing on worker nodes you don't manage) execute the 4 filter tasks in parallel across 4 cores.
5. **De-allocation:** As soon as the filter is finished and the results are returned, the executors are released back to the global pool for other users.

### 4. Why Serversless for Spark?

The biggest benefit is that it solves the **"Small File" or "Small Job" overhead**. In a classic setup, starting a cluster to process a 10MB file is a waste of time and money; in serverless, the "Hidden Cost" of metadata discovery and boot-up is minimized because the infrastructure is already running.

While both provide a serverless experience, the primary difference lies in the **interface**, the **optimization engine**, and the **persona** they serve.

## Serverless for SQL Warehouse and Notebooks

### 1. Serverless SQL Warehouse (The "Analyst" Experience)

The SQL Warehouse is designed specifically for **DBSQL (Databricks SQL)** and high-concurrency BI workloads.

* **Interface:** It is primarily used through the SQL Editor or connected BI tools like Tableau and Power BI.
* **Optimization Engine:** It uses **Photon**, a vectorized execution engine written in C++, which is highly optimized for SQL operations like filters, joins, and aggregations.
* **Scaling (Instant Compute):** It features "Instant Compute," which can scale up or down in seconds to handle dozens or hundreds of concurrent users without the overhead of starting a full Spark session for each query.
* **User Persona:** Data Analysts and BI Engineers who want to write SQL and get results without worrying about any Spark configuration.

### 2. Serverless Spark Notebook (The "Data Engineer" Experience)

The Serverless Notebook is an extension of the **Data Science & Engineering** workspace.

* **Interface:** It is used through Notebooks or Workflows and supports multiple languages (Python, Scala, SQL, R).
* **Optimization Engine:** It uses the standard Spark engine (though it can also leverage Photon if enabled) to handle complex ETL, machine learning, and data preparation tasks.
* **Execution Logic:** It is designed for linear processing—running a sequence of cells or a whole pipeline—rather than handling 50 people hitting a dashboard at the same time.
* **User Persona:** Data Engineers and Data Scientists who need the flexibility of libraries (like Pandas, Scikit-learn, or PySpark) to build end-to-end pipelines.

### Comparison Summary

| Feature | Serverless SQL Warehouse | Serverless Spark Notebook |
| --- | --- | --- |
| **Primary Goal** | Fast, high-concurrency SQL queries. | Flexible ETL and ML development. |
| **Engine** | Highly optimized Photon (C++). | Standard Spark (Java/Scala). |
| **Concurrency** | Built to handle many users simultaneously. | Built for session-based, sequential execution. |
| **Libraries** | Limited to built-in SQL functions. | Full access to PyPI and Spark libraries. |

### 3. How the "Hierarchy" Differs

In a **SQL Warehouse**, the platform manages the workers and executors even more aggressively. It doesn't just assign an executor; it intelligently routes queries to pre-warmed clusters that are already optimized for that specific data size.

In a **Serverless Notebook**, you still have a logical "Driver" that you interact with, similar to the classic Spark hierarchy, but the physical worker nodes are being dynamically attached and detached from the control plane in the background.

## Cloud Management

To provide clarity, the "physical" hardware always comes from the **cloud provider** (Azure, AWS, or GCP), but the **ownership and management** of those resources differ depending on the compute type you choose.

Databricks does not own its own data centers or proprietary hardware. Instead, it uses a **"First-Party Service"** or **"Hybrid SaaS"** model where it sits on top of your cloud's infrastructure.

### 1. Interactive and Job Clusters (Classic Compute)

In what is called the **Classic Compute Plane**, the resources are provided by your cloud provider but managed by Databricks.

* **Who provides the VM?** Azure (VMs), AWS (EC2), or GCP (GKE).
* **Who owns the resources?** **You (the customer).** The virtual machines are provisioned inside **your own cloud subscription** and your own virtual network (VPC/VNet).
* **Databricks' Role:** Databricks uses its proprietary **Control Plane** to "talk" to your cloud account, tell it to turn on 5 VMs, and then it installs the Databricks Spark runtime on them.

### 2. Serverless Compute

This represents a major shift in "who" manages the resources. In **Serverless**, the infrastructure layer becomes completely invisible to you.

* **Who provides the VM?** Still the cloud provider (Azure, AWS, or GCP).
* **Who owns/manages the resources?** **Databricks.** The VMs are provisioned in a **Serverless Compute Plane** that belongs to the Databricks cloud account, not yours.
* **Databricks' Role:** Databricks maintains a large "warm pool" of pre-running instances in their own account. When you run a query, they instantly assign you some of "their" capacity, which is why it starts in seconds rather than minutes.

### Comparison Summary: Who Provides What?

| Component | Interactive/Job Clusters (Classic) | Serverless Compute |
| --- | --- | --- |
| **Physical Hardware** | Cloud Provider (Azure/AWS/GCP) | Cloud Provider (Azure/AWS/GCP) |
| **VM Ownership** | **Your** Cloud Subscription | **Databricks'** Cloud Subscription |
| **Network Location** | Your Virtual Network (VPC/VNet) | Databricks' Serverless Network |
| **Management** | Proprietary Databricks Control Plane | Proprietary Databricks Control Plane |
| **Billing** | You pay Azure/AWS for VMs + Databricks for DBUs | You pay Databricks for everything (unified DBU) |

### Why doesn't Databricks have its own hardware?

By staying "cloud-native," Databricks ensures your data never has to leave your preferred cloud ecosystem for processing (in classic mode), and they can leverage the massive scale of companies like Microsoft and Amazon to provide thousands of servers instantly.

**In short:** Databricks provides the **proprietary "brain" (Software/Runtime)** and the **orchestration**, while the cloud provider provides the **"muscle" (Hardware/VMs)**.