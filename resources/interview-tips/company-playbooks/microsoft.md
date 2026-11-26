# Microsoft Interview Playbook

## Purpose and caveats

This playbook explores enterprise system design expectations commonly discussed in Microsoft software engineering interviews. 
*Note: Any mention of specific levels (e.g., L63-L67, Senior, Principal) is based on unconfirmed, historical, or uncertain claims from public forums and aggregated candidate experiences. It is not an official company rubric or scorecard. Hiring outcomes and level placements are never guaranteed.*

## Public architecture/interview context

Microsoft's engineering culture places a heavy emphasis on building scalable, reliable, and backward-compatible solutions, largely centered around the Azure ecosystem. System design interviews often evaluate a candidate's ability to navigate these enterprise constraints.

### Azure primitives
Candidates are often expected to understand the core building blocks of the Azure cloud. This involves mapping generic architectural components to specific Azure services. For example, understanding when to use Azure Blob Storage versus Azure Data Lake Storage, or choosing between Azure Service Bus (for strict ordering and enterprise messaging) and Azure Event Hubs (for massive telemetry ingestion). Familiarity with Azure Kubernetes Service (AKS) for orchestration and Azure Front Door or Traffic Manager for global load balancing is frequently beneficial.

### Cosmos DB multi-model/consistency options
Azure Cosmos DB is Microsoft's globally distributed, multi-model database service. A critical aspect of Cosmos DB is its nuanced approach to data consistency, offering five well-defined levels: Strong, Bounded Staleness, Session, Consistent Prefix, and Eventual. 
Understanding the trade-offs of each is a common interview topic. For instance, Strong consistency ensures reads always see the latest writes but incurs higher latency and lower availability. Session consistency, the default, provides a good balance for user-centric applications, while Bounded Staleness guarantees reads are not too far behind writes.

### Enterprise reliability
Serving large enterprises and governments requires strict reliability standards that go beyond basic high availability. Designs must factor in Disaster Recovery (DR), establishing Recovery Time Objectives (RTO) and Recovery Point Objectives (RPO) for cross-region failures. Reliability also extends to security and compliance, integrating Role-Based Access Control (RBAC), data encryption, and auditing to comply with regulations (e.g., GDPR, HIPAA).

### Backward compatibility
Enterprise customers expect that software updates will not break their existing workflows or integrations. In system design discussions, addressing how a system evolves over time without causing disruption is crucial. This involves strategies for API versioning, safe database schema migrations, feature flags, and side-by-side deployments. Relying on "flag day" migrations (where all clients must update simultaneously) is generally viewed unfavorably.

### Unofficial L63-L67 Expectations
*Note: The following level expectations are anecdotal, candidate-reported, and compiled from public forums. They are not an official company rubric, scorecard, or hiring guarantee.*

Based on public forums, L63-L64 (Senior) interviews often heavily emphasize trade-off navigation, such as diving deep into multi-region reliability and Cosmos DB consistency choices. For L65-L67 (Principal and Partner), the focus typically shifts to enterprise scale, strict compliance, isolation for multi-tenant architectures, and safe rollout strategies that explicitly avoid "flag day" migrations.

## Sources consulted

- **Consistency levels in Azure Cosmos DB**  
  Direct URL: https://learn.microsoft.com/en-us/azure/cosmos-db/consistency-levels  
  Access Date: 2026-10-23  

- **Choose an Azure compute service**  
  Direct URL: https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/compute-decision-tree  
  Access Date: 2026-10-23  

- **Reliability in Azure**  
  Direct URL: https://learn.microsoft.com/en-us/azure/reliability/  
  Access Date: 2026-10-23

## Candidate preparation

*Note: Any suggestions for preparation are derived from public Azure documentation and community-shared interview experiences. They do not constitute official Microsoft guidelines or guarantee hiring success. Unofficial levels like L63-L67 are strictly for contextual preparation.*

To prepare effectively for a Microsoft system design interview, focus on the following core areas:
- **Azure Primitives:** Build a strong mapping of generic architecture components to Azure-specific services. Be ready to articulate when to use **Azure Blob Storage** versus **Azure Data Lake Storage (ADLS)**, or when to rely on **Azure Service Bus** (for strict ordering/enterprise messaging) as opposed to **Azure Event Hubs** (for massive, high-throughput telemetry ingestion). 
- **Compute and Orchestration:** Familiarize yourself with **Azure Kubernetes Service (AKS)** for scalable microservices orchestration, and **Azure Front Door** or **Traffic Manager** for global routing and load balancing.
- **Cosmos DB Consistency:** Deeply understand Azure Cosmos DB's five consistency models (Strong, Bounded Staleness, Session, Consistent Prefix, Eventual). Be prepared to discuss the specific trade-offs of Strong (higher latency, lower availability) versus Session (balance for user-centric apps).
- **Enterprise Reliability:** Focus heavily on Disaster Recovery (DR), defining cross-region Recovery Time Objectives (RTO) and Recovery Point Objectives (RPO), and ensuring security compliance with Role-Based Access Control (RBAC).
- **Backward Compatibility:** Practice designing migration strategies that explicitly avoid disruptive "flag day" migrations, favoring API versioning, safe schema rollouts, and side-by-side deployments.

## Practice scenario: Enterprise Auditing Log System

**Requirements and Constraints:**
Design a global enterprise auditing log ingestion and querying system for financial institutions. The system must handle a peak write throughput of 100k TPS. Strict compliance requires that logs are immutable, highly available across multiple regions, and support Role-Based Access Control (RBAC).

**Design Trade-offs:**
1. **Azure Event Hubs vs. Azure Service Bus:** Choosing Event Hubs for the massive 100k TPS telemetry ingestion (due to partitioned consumer models optimized for high throughput), rather than Service Bus, which is better suited for complex enterprise messaging requiring strict ordering and transactional guarantees but might bottleneck at this scale.
2. **Cosmos DB (Strong vs. Session Consistency):** For the metadata and querying layer, deciding between Strong consistency (ensuring absolute correctness but risking higher latency and lower availability during network partitions) versus Session consistency. Given the auditing context, Strong consistency or Bounded Staleness might be necessary for immediate cross-region compliance verification, despite the performance hit.
3. **Azure Data Lake Storage (ADLS) vs. Azure Blob Storage:** Storing the immutable raw audit logs in ADLS for hierarchical namespace querying and analytics integration, rather than standard Blob Storage, which is flatter and less optimized for complex enterprise log analysis at scale.

**Failure/Edge Case:**
- **Cross-Region Total Failure:** A complete outage in the primary Azure region while processing a massive batch of compliance logs.
- **Defensible Resolution:** Implement a multi-region active-passive or active-active architecture using Azure Front Door to route traffic. Data is asynchronously or synchronously replicated to the secondary region based on RPO limits. On primary failure, the system fails over, ensuring consumers read from the secondary Cosmos DB and Event Hubs namespaces.

## Self-review rubric

*Note: This rubric is entirely candidate-created guidance based on aggregated public interview experiences. It is not an official Microsoft scorecard, rubric, or evaluation metric.*

| Dimension | L4 (Intuitive Minimum) | L5 (Trade-offs & Scale) | L6/L7 (Enterprise/Failure Scenarios) |
| :--- | :--- | :--- | :--- |
| **Azure Ecosystem Mapping** | Mentions generic databases/queues (e.g., MySQL, Kafka). | Correctly maps to Azure services (e.g., Cosmos DB, Event Hubs) with basic justifications. | Deeply contrasts specific Azure primitives (e.g., Event Hubs vs Service Bus; ADLS vs Blob) with limits and enterprise contexts. |
| **Enterprise Reliability** | Mentions basic replication and backups. | Configures multi-region failover and discusses RTO/RPO trade-offs. | Explains cross-region DR strategies, strict compliance (RBAC, immutable storage), and handles edge-case partial outages. |
| **Backward Compatibility** | Recommends pausing the system for upgrades ("flag day"). | Proposes basic API versioning and phased rollouts. | Architects side-by-side deployments, dual-write migrations without downtime, and backwards-compatible schema evolutions. |
| **Trade-off Articulation** | Picks a technology without justifying alternatives. | Compares two options (e.g., Strong vs Eventual consistency) based on latency. | Articulates nuanced trade-offs (e.g., Session vs Bounded Staleness in Cosmos DB) factoring in cost, SLAs, and enterprise compliance. |

## Sample answer outlines

### 1. Design Scenario: Enterprise Auditing Log System
- **Clarification:** Acknowledge the 100k TPS requirement and the strict compliance/immutability constraints. Establish RTO/RPO expectations for disaster recovery.
- **High-Level Architecture:** Propose Azure Front Door routing to regional API gateways (AKS). Data flows into Azure Event Hubs for high-throughput ingestion.
- **Storage/Data Model:** Route raw, immutable logs to Azure Data Lake Storage (ADLS) for hierarchical querying. Use Cosmos DB for fast metadata indexing and retrieval.
- **Trade-offs (Reasoning):** Explicitly justify Event Hubs over Service Bus to handle the 100k TPS without bottlenecking. Argue for Strong or Bounded Staleness consistency in Cosmos DB to meet strict financial auditing constraints, acknowledging the latency cost.
- **Resiliency & Compliance:** Explain the multi-region failover strategy. Detail how RBAC is applied at the ADLS and Cosmos DB layers to ensure only authorized compliance officers can query specific log partitions.

### 2. Technical/Behavioral Follow-up: Zero-Downtime Migration
- **Scenario:** The interviewer asks how you would migrate the legacy on-premises SQL Server auditing database to Cosmos DB without a "flag day" migration.
- **Initial Phase (Dual Writes):** Propose modifying the application to write to both the legacy SQL Server and the new Cosmos DB. Keep SQL Server as the primary read source.
- **Backfill & Verification:** Run a background process to backfill historical data. Implement an asynchronous verification script that compares reads from both databases to ensure data consistency.
- **Trade-offs (Reasoning):** Discuss the risk of dual-write failures (e.g., write succeeds in SQL, fails in Cosmos) and propose a resilient dead-letter queue or retry mechanism.
- **Phased Rollout:** Gradually shift read traffic (e.g., 1%, 10%, 100%) to Cosmos DB using feature flags, monitoring error rates and latency. Avoid a "flag day" by maintaining the ability to instantly rollback to SQL Server if issues arise, before eventually decommissioning the legacy database.
