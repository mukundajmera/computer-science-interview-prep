# Video Streaming — Interview Approach

## 1. Lock Scope

- Confirm VOD scope and resumable upload requirement.
- Separate metadata, blob, and playback responsibilities.

## 2. Estimate Scale

- Upload ingestion throughput and blob growth.
- Playback concurrency and egress profile.

## 3. Define APIs and Entities

- Upload session lifecycle APIs.
- Entities: `UploadSession`, `VideoAsset`, `Manifest`, `ProcessingJob`.

## 4. Draw Architecture

- Upload path to object storage and processing queue.
- Playback path through CDN and manifest service.

## 5. Deep Dives

1. Resumable multipart upload safety.
2. Processing pipeline orchestration.
3. CDN strategy and cache behavior.

## 6. Wrap-Up

- Re-state availability-first playback and durability of upload state.
