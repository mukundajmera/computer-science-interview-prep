# Distributed Object Storage - Problem Statement

## Problem Context
Design a distributed object storage system similar to Amazon S3 or Google Cloud Storage. The system should allow users to reliably store, retrieve, and manage massive amounts of unstructured data (objects) within isolated namespaces (buckets). The design must handle exabyte-scale growth while maintaining extremely high durability and availability.

## Core Requirements

### Functional Requirements
- **Bucket Operations:** Users should be able to create, delete, and list buckets.
- **Object CRUD:** Users should be able to upload (PUT), download (GET), and remove (DELETE) objects.
- **Object Versioning:** The system must support object versioning to recover from accidental deletions or overwrites. This includes using TIMEUUID ordering and delete markers.
- **Multipart Upload:** For large files, the system must support multipart uploads (initiate, upload parts in parallel, and complete assembly).
- **Prefix-based Listing:** Users should be able to list objects within a bucket using a prefix (similar to a directory structure).

### Non-Functional Requirements
- **Durability:** $99.999999999\%$ (11 nines) via Erasure Coding, or at minimum $99.9999\%$ (6 nines) using 3x replication.
- **Availability:** $99.99\%$ uptime for object reads and writes.
- **Scale:** Capable of storing $100\text{ PB}$ of data globally, comprising roughly $0.68\text{B}$ objects. Traffic scaling to $10,000\text{ write QPS}$ and $100,000\text{ read QPS}$.
- **Storage Efficiency:** The system must eliminate small-file OS inode exhaustion and wasted block fragments by packing small objects into append-only block containers.

### Out of Scope
- Object lifecycle management (e.g., auto-archiving to cold storage like Glacier).
- Access Control Lists (ACLs) and complex IAM policies.
- Cross-region replication (active-active multi-region syncing).
- Event notifications (e.g., triggering Lambda on object creation).
