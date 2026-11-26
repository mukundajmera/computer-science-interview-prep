# Problem Statement: Distributed Cloud Storage (S3)

## System to Design
Design a distributed object storage system similar to Amazon S3.

## Core User Value
Provide highly durable, available, and infinitely scalable storage for unstructured data (objects) accessed via a REST API.

## Functional Requirements
- **PutObject:** Upload a new object or overwrite an existing object.
- **GetObject:** Retrieve an object by its key.
- **DeleteObject:** Delete an object.
- **ListBucketObjects:** List all object keys in a given bucket.
- **Multipart Upload:** Support uploading large files in parallel chunks and assembling them.

## Non-Functional Requirements
- **Durability:** 99.999999999% (11 9s) - strict durability guarantee.
- **Availability:** 99.99% uptime.
- **Consistency:** Strong read-after-write consistency (for PUTs of new objects and overwrites).
- **Scalability:** Must support elastic scale-out to exabytes of data.

## Traffic and Storage Sizing
- **Initial Capacity:** 100 Petabytes (PB).
- **Read QPS:** 50,000 requests per second.
- **Write QPS:** 5,000 requests per second.
