# Snowflake Cloud Data Warehouse Case Study

## 1. Problem Statement

Snowflake set out to rebuild the analytical data warehouse for the cloud era. Traditional warehouses were designed for owned hardware: fixed clusters where storage and compute scale together in lockstep. That model breaks down when data volume and query demand grow at different rates.

### Business Challenge
Analytics teams want to load everything and ask questions later. Data volumes grow relentlessly, but query demand is spiky: a morning burst of dashboard refreshes, a month-end reporting spike, long idle nights. A cluster sized for the peak sits mostly idle and expensive. A cluster sized for the average makes the peak unusably slow. On top of that, different teams (data engineering, analysts, data scientists) fight over the same compute, so one heavy workload degrades everyone else's dashboards.

### Technical Requirements
- **Independent scaling of storage and compute:** Add petabytes of data without buying compute, and add compute without copying data.
- **Workload isolation:** ETL, BI dashboards, and ad-hoc data science must not contend for the same resources.
- **Elasticity:** Compute must scale up, down, and out in seconds, and cost nothing when idle.
- **Correctness and concurrency:** Full ACID transactions with many readers and writers at once.
- **Time travel and recovery:** Query historical table states and recover from accidental drops without backups or restore jobs.
- **Near-zero administration:** No manual index building, partition pruning design, vacuum tuning, or capacity forecasting.

### Scale Metrics
- **Customers:** Thousands of enterprises run production analytics on the platform.
- **Query volume:** Hundreds of millions of queries per day across the fleet (publicly discussed order of magnitude; treat any finer number as an illustrative estimate).
- **Data volume:** Many petabytes per large customer, stored as compressed columnar data in cloud object storage.
- **Concurrency:** A single account can run many independent compute clusters at once, each sized from one node to hundreds of nodes.

Numbers below that are not widely published are labelled as illustrative estimates with the arithmetic shown.

---

## 2. Architecture Evolution

The design only makes sense against the two architectures that came before it.

### Phase 1: Shared-Disk Warehouses
Early enterprise warehouses put all data on one shared storage array and gave every compute node access to it.
- **Pros:** No data movement when adding a node; simple failure model.
- **Cons:** The storage interconnect becomes the bottleneck. Nodes cache aggressively, and cache coherence traffic grows with cluster size. Scaling beyond a few dozen nodes is impractical.

### Phase 2: Shared-Nothing MPP
Massively parallel processing systems (the classic on-premise answer) partition data across nodes. Each node owns its slice on local disk and processes queries over its own partition.
- **Pros:** Linear scale-out for scans and joins while data stays balanced.
- **Cons:** Storage and compute are fused. To add storage you add nodes (and pay for compute you may not need). To add compute you must physically rebalance data across nodes, an hours-long operation. Upgrades, failures, and elasticity all fight the fused model.

### Phase 3: Separated Storage and Compute (Snowflake's Design)
Snowflake rebuilt the warehouse around cheap, durable cloud object storage and stateless compute:
- **Storage** lives in the cloud provider's object store (S3, Azure Blob, or Google Cloud Storage) in a proprietary compressed columnar format.
- **Compute** is organized into *virtual warehouses*: independent MPP clusters that all read and write the same shared data, with no data movement between them.
- **Cloud services** is a multi-tenant control plane that authenticates users, parses and optimizes SQL, manages transactions and metadata, and coordinates everything.

Because object storage is effectively infinite and compute clusters hold no authoritative state, either side scales without touching the other. This is the central decision everything else in this case study follows from.

---

## 3. The Three-Layer Architecture

### Layer 1: Database Storage
All table data is persisted in cloud object storage, which the platform rents from the underlying cloud provider.
- Objects are immutable: a write creates new objects rather than mutating existing ones. Immutability is what makes time travel and zero-copy cloning cheap (covered in section 8).
- Durability and replication across availability zones are delegated to the object store, which is engineered for extreme durability. The warehouse layer inherits those guarantees instead of reimplementing them.
- Data is encrypted at rest, compressed, and organized into columnar files. Customers cannot address the files directly; all access goes through Snowflake's engine, which keeps the format free to evolve.

### Layer 2: Query Processing (Virtual Warehouses)
A *virtual warehouse* is a named, independent MPP compute cluster.
- Each warehouse has its own worker nodes with local SSD used purely as a data cache for recently read micro-partitions, not as authoritative storage.
- Warehouses are sized in discrete "t-shirt" steps (doubling node counts per step) and can also scale out by adding clusters under load.
- One warehouse's heavy ETL job has zero performance effect on another warehouse's dashboard queries. They contend on nothing except the data itself, which is shared read-mostly.
- A warehouse consumes credits only while running. Auto-suspend parks it after an idle window; auto-resume restarts it on the next query, typically in seconds.

### Layer 3: Cloud Services
The always-on, multi-tenant control plane.
- **Authentication and access control:** Sessions, role-based access control down to columns and rows.
- **Query parsing and optimization:** SQL is parsed, planned, and cost-optimized here before any compute cluster sees it.
- **Transaction and metadata management:** The metadata catalog (accounts, tables, micro-partition statistics, transaction state) lives here, not in the warehouses.
- **Infrastructure management:** Provisioning, health checks, and upgrades of the warehouse fleet.

The separation matters for interviews: the optimizer and transaction coordinator are shared services, while execution capacity is private per workload. That is the opposite of shared-nothing MPP, where both were fused per node.

---

## 4. Micro-Partitions and Pruning

Snowflake's fundamental storage unit is the **micro-partition**, and understanding it is the key to understanding why the system needs no indexes.

### What a Micro-Partition Is
- Each table's data is stored as a set of micro-partitions: contiguous units of roughly 50-500 MB of uncompressed data (the commonly cited range; compressed on disk they are far smaller).
- Within a micro-partition, data is stored column-by-column and compressed individually per column.
- Micro-partitions are written immutably and automatically as data arrives. Users do not create, name, or manage them.

### The Metadata Layer Makes Pruning Possible
For every micro-partition, the metadata catalog records per-column statistics: the min and max value, the distinct-count sketch, and null counts. Because this metadata lives in the cloud services layer, the optimizer can decide which partitions a query must read **without starting any compute at all**.

### How Pruning Skips Data
A query with a selective predicate reads only the partitions whose min/max ranges can contain matching values.

Worked example (illustrative estimate, arithmetic shown):
- A table holds 10 TB uncompressed across micro-partitions averaging 100 MB uncompressed each: 10 TB / 100 MB = 100,000 micro-partitions.
- A query filters `WHERE order_date = '2026-01-15'` on data that is naturally date-ordered by ingest.
- Only partitions whose date range includes that day survive pruning. If data is well ordered, roughly one day out of a 3-year table: about 1/1000 of partitions, so ~100 partitions, ~10 GB read instead of 10 TB.
- The scan is 1000x smaller with no index, no partition scheme, and no DBA involvement.

### When Pruning Does Not Help
Pruning is only as good as the correlation between the filter column and physical layout. Two failure modes are worth naming:
- **Filter on a high-cardinality, uncorrelated column:** A predicate like `WHERE customer_id = 12345` where customer IDs are randomly distributed across partitions. Every partition's min/max range contains the value, so nothing is pruned and the scan reads all 100,000 partitions. A B-tree index in a row store would have answered this in a handful of page reads; this is the honest cost of the pruning-only design, and the reason selective filters on clustered columns are the workload Snowflake is built for.
- **Skewed data:** If one day holds 10% of all rows, its partitions dominate every date scan regardless of ordering.

The mitigation when a workload genuinely needs point lookups is either a search-optimization service (a maintained access path the vendor offers for selective equality lookups) or keeping the hot serving path in an OLTP system and using the warehouse for what it is for: scans and aggregations.

### Clustering and Its Limits
Natural ingest order gives good clustering for free. When a table's query patterns do not match ingest order, a clustering key can be declared and a background service rewrites partitions over time to improve colocation. The trade-off: reclustering consumes credits and rewrites immutable partitions, so it is justified only for very large tables with stable, selective query patterns. This is a deliberate "measure first, then pay" design.

---

## 5. Virtual Warehouses in Depth

### Independent MPP Execution
Within one warehouse, a query executes massively parallel: the optimizer's plan is split into fragments distributed across the warehouse's worker nodes, each scanning a subset of the surviving micro-partitions. Intermediate results flow between nodes for joins and aggregations.

### Elasticity Levers
- **Scale up:** Resize a warehouse (for example from 2 nodes to 4, doubling per step) to speed up a single complex query. Resizing a running warehouse is allowed and does not move data, because data is not attached to the warehouse.
- **Scale out:** Multi-cluster warehouses add or remove whole clusters as concurrent query load rises and falls, keeping queue times bounded during bursts.
- **Scale to zero:** Auto-suspend stops credit consumption entirely. The common billing shape is per-second with a short minimum (60 seconds is the commonly cited figure) on each resume.

### Local Caching
Each worker node caches the remote micro-partitions it has read on its local SSD. A repeated or overlapping query on the same warehouse then reads warm local disk instead of remote object storage. When a warehouse suspends, this cache is dropped; the design accepts a cold start on resume in exchange for paying nothing while idle.

### A Sizing Example
Choosing a warehouse size is an empirical loop, not a formula, but the shape of the decision is stable. Illustrative estimate, arithmetic shown:
- A nightly ETL job reads 200 GB of micro-partition data and aggregates it. On a 2-node warehouse it takes 60 minutes.
- Doubling to 4 nodes roughly doubles per-second credit cost but, for a parallel-friendly scan, roughly halves runtime: 4 nodes * 30 minutes = the same 2 node-hours of compute, so roughly the same credit spend for results in half the wall-clock time.
- The scaling stops being linear when the query has serial phases (a final single-node sort, a small join side) or when partitions per query outnumber useful workers. Past that point, more nodes buy latency, not efficiency, and credits grow faster than runtime shrinks.

This is why the standard advice is to start small, measure, and resize: because compute is stateless and decoupled from data, a resize is a configuration change, not a migration.

---

## 6. The Metadata and Cloud Services Layer

The metadata catalog is the quiet workhorse of the architecture.
- **What it holds:** Every table's micro-partition list with per-column min/max statistics, transaction visibility information, user and role definitions, and query history.
- **Why it is fast:** Partition pruning, cost estimation, and result-cache lookups are all pure metadata operations in the control plane, answered in milliseconds before any warehouse is involved.
- **Why it matters for correctness:** Transactions commit by atomically publishing a new set of partition references in the catalog. Old partition versions are not modified; they simply stop being visible to new transactions. MVCC falls out of immutability.

This is also where **zero administration** comes from: statistics are maintained automatically on every write, so there is no ANALYZE step, no index to build, and no partition key to design.

---

## 7. Result Caching

Snowflake caches at three distinct levels, and keeping them separate is a common interview differentiator:

1. **Result cache (cloud services):** The full result set of an executed query is persisted for a retention window (24 hours is the commonly cited figure). If the identical query text arrives again and the underlying data has not changed, the result is returned from the cache with no warehouse running at all, costing zero compute credits.
2. **Local disk cache (virtual warehouse):** Recently read micro-partitions on worker SSDs, described in section 5. Dropped on suspend.
3. **Metadata cache (cloud services):** Partition statistics used for pruning, always warm in the control plane.

The result cache is what makes interactive dashboard loops feel instant: the first refresh computes, subsequent identical refreshes are free until the data changes.

---

## 8. Time Travel and Zero-Copy Cloning

Because micro-partitions are immutable, history is free to keep.

### Time Travel
- Queries can reference a table **as of** a timestamp, a time offset, or a past query ID. The engine simply resolves the table's partition list as it existed at that point, all through metadata.
- The retention window depends on the edition: 1 day is the commonly cited default, extendable up to 90 days on higher editions.
- Dropped tables and schemas are recoverable within the window with an UNDROP command, replacing restore-from-backup for most accidents.
- Beyond the time travel window, a further fail-safe period (7 days is the commonly cited figure) keeps data recoverable by the vendor for disaster scenarios.

### What It Looks Like in Practice
Time travel is ordinary SQL with an AT or BEFORE clause, which matters for interviews: recovery is a query, not a ticket to a storage team.
- Audit a value as it stood an hour ago: `SELECT * FROM orders AT(OFFSET => -3600);`
- Rebuild a table from the moment before a bad job ran: `CREATE TABLE orders_restored CLONE orders AT(TIMESTAMP => '2026-01-15 13:59:00');`
- Undo a drop: `UNDROP TABLE orders;`

Each of these resolves through the metadata catalog against immutable partitions. No files are copied, no restore job runs, and concurrent workloads are unaffected, because the historical partitions were never modified in the first place.

### Zero-Copy Cloning
A clone of a table, schema, or entire database is created in seconds regardless of size, because cloning copies only metadata: the clone points at the same immutable micro-partitions. New writes on either side create new partitions. Storage is charged only for partitions that diverge.

Worked example (illustrative estimate, arithmetic shown):
- Clone a 5 TB production table for a development environment: creation takes seconds and adds 0 bytes.
- Developers rewrite 1% of the data: new partitions hold 5 TB * 1% = 50 GB. The dev environment costs 50 GB of extra storage, not 5 TB.
- The same workflow on a copy-on-write-absent system costs a full 5 TB copy and hours of provisioning.

---

## 9. The Cost Model That Follows

The architecture produces a two-axis cost model, and it is a frequent interview topic because it inverts on-premise intuition.

### Storage Axis
- Billed per terabyte per month of compressed data stored, at cloud-storage-like rates.
- Time travel and fail-safe retention add storage, so retention windows are a cost lever.

### Compute Axis
- Billed in credits consumed per second per running warehouse, with larger sizes consuming proportionally more credits per second.
- Idle warehouses auto-suspend and consume nothing.
- Cloud services usage below a daily allowance relative to warehouse spend is typically included (the commonly cited allowance is 10% of daily warehouse credits); heavy metadata-only usage beyond that is billed.

### Consequences
- **Cost follows concurrency, not capacity.** A team pays for the minutes its warehouses run, not for a peak-sized cluster owned all month.
- **Spiky workloads win the most.** Nightly ETL that runs 2 hours a day pays for 2 hours a day.
- **Misconfiguration is the main cost risk.** A warehouse left without auto-suspend burns credits around the clock; a multi-cluster warehouse sized for Black Friday and forgotten is the classic bill shock.

Worked example (illustrative estimate, arithmetic shown):
- A dashboard team needs a medium warehouse 3 hours per weekday: 3 h * 22 days = 66 warehouse-hours per month.
- An always-on on-premise-equivalent cluster bills for 24 * 30 = 720 hours.
- Same compute capacity, roughly 9% of the compute-hours: 66 / 720.

---

## 10. Key Design Decisions & Technologies

| Component | Decision | Rationale |
| :--- | :--- | :--- |
| **Storage substrate** | Cloud object storage (S3 / Azure Blob / GCS), immutable files | Inherits extreme durability and effectively unlimited capacity; immutability enables MVCC, time travel, and cloning |
| **Storage unit** | Micro-partitions (~50-500 MB uncompressed) with per-column statistics | Pruning replaces hand-built indexes; statistics maintained automatically on write |
| **Compute** | Independent virtual warehouses, stateless MPP clusters | Workload isolation and per-workload elasticity with zero data movement |
| **Control plane** | Multi-tenant cloud services layer owning metadata, optimization, and transactions | Pruning and result-cache decisions without spinning up compute |
| **Caching** | Three independent levels: result, local disk, metadata | Each level targets a different latency/cost point |
| **Billing** | Per-second credits for compute, per-TB-month for storage | Cost tracks actual use; idle time is free |

---

## 11. Trade-offs Made

1. **Latency on cold start vs. zero idle cost:** Auto-suspend saves money but the first query after resume pays warehouse startup and a cold local cache. Interactive teams often accept a longer suspend window, trading money for responsiveness.
2. **Object-store latency vs. elasticity:** Remote storage has higher per-read latency than local disk in shared-nothing systems. Snowflake accepts this and buys it back with the local SSD cache and aggressive pruning, which reduces the total bytes read far below what a local-disk system scans.
3. **Automatic clustering vs. write amplification:** Background reclustering improves pruning for selective queries but rewrites immutable partitions, costing credits and storage churn. It is opt-in and measured, not default.
4. **Managed format vs. openness:** The proprietary micro-partition format lets the engine evolve freely but means data is only readable through the engine. Export paths exist; direct file access does not.
5. **Centralized metadata vs. control-plane scale:** A shared catalog makes pruning and MVCC elegant, but the cloud services layer itself must scale as a multi-tenant service, which is why heavy metadata operations have their own billing allowance.

---

## 12. Lessons Learned

- **Separate what scales differently.** Storage grows monotonically; compute demand is spiky. Fusing them forces the worst of both.
- **Immutability buys features, not just safety.** MVCC, time travel, zero-copy clones, and cheap retries all fall out of "never update in place."
- **Metadata is a first-class query engine.** The fastest scan is the one you never run. Investing in always-fresh statistics removes the need for user-managed indexes entirely.
- **Elasticity is a billing model, not just an architecture.** Per-second credits are what make scale-to-zero real; without them, idle capacity is invisible cost.
- **Isolation beats tuning.** Giving each workload its own warehouse eliminates whole categories of "noisy neighbor" performance debugging that plague shared clusters.
- **Charge models shape behavior.** Because compute is metered per second and storage per terabyte, teams naturally ask whether a workload should run at all, a question that fixed on-premise clusters never forced. Treating cost as a first-class metric alongside latency and correctness is a lesson that transfers to every cloud system design.

---

## 13. Staff Interview Questions & Scoring Rubrics

### Question 1: Design a warehouse for spiky, multi-team analytics
**Prompt:** A company has three teams (ETL, BI, data science) sharing one on-premise MPP cluster. Nightly ETL slows the morning dashboards, and the data scientists' ad-hoc scans starve everyone. Design the cloud replacement.

**Scoring Rubric:**
- **Red Flags (Fail):** Scales the single cluster up vertically. Suggests separate physical copies of the data per team.
- **Acceptable (Pass):** Separates storage and compute. Gives each team an isolated compute cluster over shared storage. Mentions auto-suspend to stop paying for idle time.
- **Excellent (Strong Hire):** Adds the pruning story (per-partition min/max statistics replacing indexes), explains that isolation works because compute is stateless and data is shared, and addresses the cost model: per-second credits, scale-out under concurrency, and the risk of forgotten running warehouses.

### Question 2: Why does this system need no indexes?
**Prompt:** A DBA from a traditional warehouse asks where to declare indexes and partition keys. Explain how queries stay fast without them.

**Scoring Rubric:**
- **Red Flags (Fail):** Claims data is just "indexed internally" without specifics. Suggests full table scans are acceptable at petabyte scale without explanation.
- **Acceptable (Pass):** Describes micro-partitions with per-column min/max metadata and pruning that skips irrelevant partitions.
- **Excellent (Strong Hire):** Quantifies pruning with a worked example (partitions surviving = table size / selectivity), explains natural clustering from ingest order, knows when a declared clustering key and background reclustering pay off, and contrasts this with manual partition scheme design in older systems.

### Question 3: Recover from a dropped production table
**Prompt:** An engineer drops a 5 TB production table at 14:00 and notices at 15:30. Walk through recovery options and their costs.

**Scoring Rubric:**
- **Red Flags (Fail):** Reaches for restore-from-backup as the only option. Claims the data is simply gone.
- **Acceptable (Pass):** Knows time travel can query or undrop the table within its retention window.
- **Excellent (Strong Hire):** Explains *why* it is cheap (immutable partitions plus metadata-only version resolution), knows the typical retention defaults and how edition changes them, distinguishes time travel from the fail-safe period, and discusses zero-copy cloning as the related primitive for instant environment provisioning.

---

## 14. Interview Relevance

- **Data engineering and analytics roles:** Directly relevant for any company building on a cloud warehouse or lakehouse.
- **System design interviews:** The canonical example of storage/compute separation, alongside object storage design and metadata-driven query planning.
- **Cost-conscious architecture discussions:** A ready-made case for elasticity, scale-to-zero, and cost-as-a-design-goal.
- **Contrasts well with:** Shared-nothing systems (classic MPP), the Stripe ledger's write-optimized OLTP design, and Spanner's globally consistent OLTP approach. Together these three cover the points on the data-systems design triangle that staff interviews return to most often: elastic analytical scans, high-integrity writes, and global consistency.

---

## 15. Related Repo Content

### Similar HLD Projects and Concepts
- [Distributed Cloud Storage (S3)](../../04-hld-projects/distributed-cloud-storage-s3/)
- [Distributed Object Storage - Problem Statement](../../04-hld-projects/distributed-object-storage/)
- [Database Sharding](../../03-hld-concepts/database-sharding/)
- [Data Partitioning](../../03-hld-concepts/data-partitioning/)
- [Caching](../../03-hld-concepts/caching/)

## 📊 Diagrams

- [Three-layer architecture](diagrams/architecture.mmd) - cloud services layer with the metadata catalog and result cache, independent virtual warehouses, and centralized micro-partition storage.

---

## 📚 Provenance and Sources

This case study uses widely known public facts about Snowflake's architecture: the three-layer design, micro-partitions with automatic per-column statistics, virtual warehouses with per-second credit billing, result caching, time travel, and zero-copy cloning are all documented in Snowflake's public documentation, marketing materials, and conference talks. Figures noted as "commonly cited" (the 50-500 MB micro-partition range, the 24-hour result cache, the 1-day default and 90-day maximum time travel windows, the 7-day fail-safe period, the 60-second resume minimum, and the 10% cloud services allowance) are long-standing public values that the vendor can change; verify against current documentation before quoting in a design document. All worked examples are illustrative estimates with the arithmetic shown.

*End of Case Study*
