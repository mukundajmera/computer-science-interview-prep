# Code Walkthrough: Distributed Cloud Storage (S3) Simulation Contract

This document outlines the bounded educational model for the Distributed Cloud Storage (S3) simulator. This simulation is intended for offline educational purposes and does not contain the complexities of a true distributed production environment.

## 1. Bounded Stages and APIs

The simulation suite comprises three primary implementation modules:

### Stage 1: `S3StorageService` (Core Object Operations)
This module simulates the core object storage functionality, focusing on metadata tracking and bucket interactions.

**APIs:**
*   `createBucket(bucketName: String)`: Initializes a logical bucket container.
*   `deleteBucket(bucketName: String)`: Removes a logical bucket.
*   `putObject(bucketName: String, key: String, data: byte[]): String`: Uploads a new object or overwrites an existing one, returning a unique `versionId`.
*   `getObject(bucketName: String, key: String, versionId: String?): byte[]`: Retrieves an object by its key. Defaults to the latest version if `versionId` is omitted.
*   `getObjectWithRange(bucketName: String, key: String, versionId: String?, start: int, end: int): byte[]`: Retrieves a specific byte range of the object data.
*   `deleteObject(bucketName: String, key: String): String`: Performs a soft delete by creating a delete marker, returning a new `versionId`.
*   `listBucketObjects(bucketName: String): List<String>`: Lists all object keys in a given bucket.

**Invariants & Guarantees:**
*   **Success:** A successful `putObject` immediately makes the object available for `getObject` (simulating strong read-after-write metadata consistency).
*   **Success:** `getObjectWithRange` correctly handles valid partial byte requests.
*   **Success:** `listBucketObjects` returns a list of all object keys in a bucket.
*   **Failure:** `getObject` raises an error if the bucket doesn't exist, the object doesn't exist, or the object has been soft-deleted (the latest version is a delete marker).
*   **Failure:** `getObjectWithRange` raises an error on out-of-bounds byte range requests.
*   **Failure:** `listBucketObjects` raises an error if the bucket doesn't exist.

### Stage 2: `MultipartUploadManager` (Large File Assembly)
This module simulates the process of uploading large files in parallel chunks and reassembling them.

**APIs:**
*   `initiateMultipartUpload(bucketName: String, key: String): String`: Starts a new multipart upload session, returning a unique `uploadId`.
*   `uploadPart(uploadId: String, partNumber: int, data: byte[]): String`: Uploads a specific chunk of data, returning an MD5 `ETag` checksum.
*   `completeMultipartUpload(uploadId: String, partNumbersToComplete: List<int>): String`: Assembles the uploaded parts in ascending order, concatenates the chunks, and produces a composite `ETag`.

**Invariants & Guarantees:**
*   **Success:** Concatenating valid parts produces a composite `ETag` that reflects the number of parts (e.g., `<hash>-<num_parts>`).
*   **Success:** The assembled final object is pushed to the `S3StorageService` and becomes immediately available.
*   **Failure:** `uploadPart` raises an error for invalid part numbers or an unknown `uploadId`.
*   **Failure:** `completeMultipartUpload` raises an error if the provided part numbers are out of order, missing, or belong to an unknown `uploadId`.

### Stage 3: Pre-signed URLs (Delegated Authorization)
This stage simulates time-bound delegated access using cryptographic signatures.

**APIs (within `S3StorageService`):**
*   `generatePresignedUrl(bucketName: String, key: String, httpMethod: String, expiryMillis: long): String`: Generates an authorized URL containing an expiration time and an HMAC-SHA256 signature.
*   `verifyPresignedUrl(url: String, httpMethod: String, currentTimeMillis: long): boolean`: Validates the signature, HTTP method, and expiration time against the current clock.

**Invariants & Guarantees:**
*   **Success:** Correct signature with a valid expiry time returns `true`.
*   **Failure:** An expired URL, a tampered URL parameter, or an incorrect HTTP method returns `false`.

## 2. Normal and Failure Fixtures

The simulation is validated using the following test scenarios:

*   **Normal Fixtures:**
    *   **Bucket Operations:** Creating a bucket, putting a single object, and successfully retrieving it.
    *   **Versioning:** Uploading multiple versions of the same key and retrieving an older version by ID.
    *   **Byte Range:** Retrieving a valid subset of an uploaded object's bytes.
    *   **Listing Objects:** Putting multiple objects in a bucket and successfully listing their keys.
    *   **Multipart Upload:** Initiating an upload, supplying parts 1 and 2 (potentially out of chronological time order), and completing the upload in ascending numerical order.
    *   **Pre-signed URLs:** Generating a URL and verifying it successfully before the expiration clock ticks past the limit.

*   **Failure Fixtures:**
    *   **Missing Resources:** Attempting to retrieve from an unknown bucket or an unknown key, or attempting to list objects from an unknown bucket.
    *   **Invalid Range:** Requesting bytes outside the bounds of the object payload.
    *   **Soft Deletion:** Attempting to retrieve a key without a `versionId` immediately after calling `deleteObject` on that key.
    *   **Invalid Multipart Assembly:** Attempting to complete a multipart upload with missing parts or with an out-of-order part list.
    *   **Signature Rejection:** Altering the `expires` query parameter of a pre-signed URL and confirming `verifyPresignedUrl` rejects it.
    *   **Expiration Rejection:** Verifying a valid URL but supplying a `currentTimeMillis` that is greater than the embedded expiration timestamp.

## 3. Explicit Gaps to the Actual Service

This educational model is strictly a conceptual simulator. It intentionally abstracts away critical production complexities:

*   **Durability and Storage Location:** The simulation stores object payloads in in-memory structures (e.g., `ConcurrentHashMap`). It completely omits the physical chunking, disk JBODs, and erasure coding (e.g., Reed-Solomon) required for 11 9s of durability.
*   **Metadata Consistency:** Strong read-after-write consistency is trivially achieved using thread-safe data structures in a single process. A real deployment requires distributed consensus (e.g., Spanner, CockroachDB) and two-phase commits to coordinate metadata availability with physical blob storage.
*   **Security and Key Management:** The pre-signed URL HMAC simulation uses a hardcoded, plaintext secret key injected directly into the service. Real systems utilize centralized Key Management Services (KMS), rotating secrets, and IAM role hierarchies.
*   **Network and Wire Formats:** All simulated operations bypass HTTP parsing, serialization, load balancing, and Kafka/SQS integration. The API calls are direct in-process memory invocations.
*   **Background Maintenance:** Real deployments feature continuous background daemons for bitrot scrubbing, garbage collection of orphan chunks, and lifecycle management. These processes are entirely excluded from this bounded simulation.
