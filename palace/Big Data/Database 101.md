# Let us talk database :)

<div id="table-of-contents">
<h3>Table of Contents</h3>
<ul>
<li><a href="#database-sharding-and-partitioning">1. Database Sharding and Partitioning</a></li>
<li><a href="#database-per-service">2. Database per Service Pattern in Microservices</a></li>
<li><a href="#sharing-database">3. Sharing Databases in Microservices</a></li>
<li><a href="#github-outage">4. Database Management in Production (GitHub Outage Analysis)</a></li>
</ul>
</div>

---

<div id="database-sharding-and-partitioning"></div>

### 1. Database Sharding and Partitioning
Let us explore how databases evolve from a single node to a distributed system to handle massive scale.

**The Evolution of Scaling:**
*   **Vertical Scaling (Scale Up):** Initially, you increase the CPU, RAM, and disk of a single server to handle increased load. However, this has hardware limitations and becomes expensive.
*   **Read Replicas:** To help with read-heavy traffic, a "read replica" (follower) is added. All writes go to the master, and reads are redirected to the replica.
*   **Horizontal Scaling (Scale Out):** When vertical scaling hits a ceiling, you add more machines (shards) and split the data between them to increase throughput,.

**Definitions:**
*   **Sharding:** Occurs at the **database level**. It is the method of distributing data across multiple physical machines (shards),.
*   **Partitioning:** Occurs at the **data level**. It is the logic of splitting a gigantic dataset into smaller, mutually exclusive chunks (e.g., separating 100GB of data into five 20GB chunks).

**Merits of Sharding:**
*   **Higher Throughput:** By adding more nodes, you can linearly increase the system's ability to handle read and write traffic. For instance, two nodes can handle twice the load of one,.
*   **Increased Storage Capacity:** It overcomes the physical disk limits of a single server. If you have 200TB of data but a 100TB disk limit, sharding allows you to store the total dataset across multiple machines.
*   **High Availability:** If one shard goes down, the others may still remain operational, preventing a total system blackout.

**Demerits of Sharding:**
*   **Operational Complexity:** Managing multiple databases is difficult. You must handle replication lag and rebalance partitions if a specific shard becomes "hot" (overloaded).
*   **Expensive Cross-Shard Queries:** Joins across different shards are extremely inefficient and expensive regarding time and compute resources. Ideally, queries should be answered by a single shard,.

---

<div id="database-per-service"></div>

### 2. Database per Service Pattern in Microservices
Let us discuss the architectural pattern where every microservice owns its own independent database to promote loose coupling.

**The Concept:**
In a social network, for example, a Chat service might use a write-heavy NoSQL DB (like Cassandra), while a Relationship service uses a Graph DB (like Neo4j), and an Analytics service uses a Data Warehouse (like Delta Lake).

**Merits:**
*   **Loose Coupling:** This is the "heart and soul" of microservices. Teams can build, test, and deploy independently without breaking other services via database changes,.
*   **Polyglot Persistence (Best Tool for the Job):** You can choose a database specialized for the specific problem (e.g., ElasticSearch for search, Graph DB for social connections) rather than forcing everything into a relational DB,.
*   **Granular Scaling:** You can scale specific databases based on need. If the payment service needs strong consistency (vertical scaling) but the chat service needs high throughput (sharding), you can apply different strategies without affecting the whole system,.
*   **Fault Isolation:** If the profile database goes down, only the profile service fails. Other services, like payments, can continue to generate revenue.
*   **Compliance & Security:** You can apply strict encryption and compliance measures (like PII protection) only to the specific databases holding sensitive data, rather than encrypting the entire platform's data.

**Demerits:**
*   **Complex Cross-Service Transactions:** Implementing distributed transactions (e.g., Two-Phase Commit) is extremely complex and can reduce throughput by at least 3x due to network coordination,.
*   **Data Propagation is Difficult:** Conveying updates (e.g., a new post created) to other services (e.g., feed service) requires asynchronous messaging (queues/brokers), leading to eventual consistency rather than strong consistency.
*   **Operational Overhead:** Managing multiple types of databases (Graph, Relational, NoSQL) requires broad expertise in infrastructure monitoring, scaling, and recovery, which is a major burden for DevOps teams.

---

<div id="sharing-database"></div>

### 3. Sharing Databases in Microservices
TLet us challenge the idea that sharing a database is always an "anti-pattern" and let us see where it might be practical. 

**The Pattern:**
Multiple microservices (e.g., Blog service and Analytics service) communicate by reading and writing to the same shared physical database.

**Merits:**
*   **Simplicity & Speed:** It is the simplest way to integrate services. There is no need for complex API contracts or gRPC implementations.
*   **Performance:** There is no extra network hop or latency overhead because services talk directly to the data.
*   **Simplified Operations:** There are fewer moving parts to manage (no separate DBs, no complex connection pools for inter-service communication).
*   **Use Case:** ideal for startups, MVPs, or small teams where speed is prioritized over strict architectural purity.

**Demerits (Challenges):**
*   **Tight Coupling (Internal Details Leaked):** External services need to know the database schema (internal details). If the owning team changes the schema (e.g., table structure), it breaks the other services,.
*   **Loss of Autonomy:** The team owning the database cannot optimize or change technologies (e.g., moving to NoSQL) without coordinating with every other team that accesses that DB,.
*   **Shared Business Logic:** Logic regarding how to fetch or join data ends up replicated across multiple services, reducing cohesion.
*   **Risk of Data Corruption:** A buggy script in the Analytics service could accidentally delete or corrupt data owned by the Blog service.
*   **"Noisy Neighbor" Abuse:** A heavy query from one service can choke the database, bringing down performance for all other services.

**Mitigation: (Temporary)**
You can mitigate read-load abuse by having external services read from a **Read Replica**, keeping the master free for the primary service.

---

<div id="github-outage"></div>

### 4. Database Management in Production (GitHub Outage Analysis)
Let us understand a GitHub outage to explain the tools used to manage databases at scale: **ProxySQL** and **Orchestrator**.

**Tools & Their Merits:**

*   **ProxySQL:** A layer sitting between API servers and the database cluster.
    *   **Connection Handling:** It buffers connections, protecting the database from being overwhelmed by too many open connections from API servers.
    *   **Intelligent Routing:** It acts as a gatekeeper, seamlessly routing writes to masters and reads to specific replicas (e.g., heavy analytics queries to a specific node) without the application needing to know.
    *   **Caching:** It can cache SQL query responses to reduce database load.
    *   **Access Management:** It can generate short-lived, temporary credentials for improved security.

*   **Orchestrator:** A tool for MySQL topology management and high availability.
    *   **Topology Discovery & Visualization:** It detects master and replica relationships and visualizes the cluster.
    *   **Automated Recovery:** If a master node crashes, Orchestrator automatically promotes a replica to be the new master.
    *   **Anti-Flapping Mechanism:** This is a crucial feature that prevents **cascading failures**. If Orchestrator promotes a replica and that new master also crashes immediately, "anti-flapping" prevents it from promoting yet another replica. This stops the system from destroying all replicas one by one,.

**The Outage Lesson:**
In the GitHub incident, a ProxySQL upgrade caused the primary node to crash. Orchestrator’s anti-flapping stopped the auto-failover to save the remaining nodes. Manual recovery attempts also failed. The ultimate resolution was a **full revert** downgrading ProxySQL to the previous version