package filestorage.v2;

import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

/**
 * File Storage Service - v2-scaled
 * 
 * Enhancements over v1:
 * - Distributed caching for metadata and hot files
 * - CDN integration for static file delivery
 * - Chunked upload/download for large files
 * - Background workers for async processing
 * - Read replicas for metadata queries
 */

// ============================================================================
// Core Interfaces
// ============================================================================

interface Cache<K, V> {
    V get(K key);
    void put(K key, V value, long ttlSeconds);
    void invalidate(K key);
    boolean exists(K key);
}

interface CDNService {
    String getSignedUrl(String fileId, long expirySeconds);
    void invalidateCache(String fileId);
    void warmCache(String fileId, String objectStorageUrl);
}

interface ChunkManager {
    String initiateChunkedUpload(String fileId, long totalSize, int chunkSize);
    void uploadChunk(String uploadId, int chunkNumber, byte[] data);
    void completeChunkedUpload(String uploadId);
    void abortChunkedUpload(String uploadId);
    ChunkStatus getUploadStatus(String uploadId);
}

// ============================================================================
// DTOs
// ============================================================================

class ChunkStatus {
    private final String uploadId;
    private final List<Integer> uploadedChunks;
    private final List<Integer> pendingChunks;
    private final long totalSize;
    private final long uploadedSize;

    public ChunkStatus(String uploadId, List<Integer> uploadedChunks, 
                       List<Integer> pendingChunks, long totalSize, long uploadedSize) {
        this.uploadId = uploadId;
        this.uploadedChunks = uploadedChunks;
        this.pendingChunks = pendingChunks;
        this.totalSize = totalSize;
        this.uploadedSize = uploadedSize;
    }

    public String getUploadId() { return uploadId; }
    public List<Integer> getUploadedChunks() { return uploadedChunks; }
    public List<Integer> getPendingChunks() { return pendingChunks; }
    public long getTotalSize() { return totalSize; }
    public long getUploadedSize() { return uploadedSize; }
    public double getProgressPercent() { return (uploadedSize * 100.0) / totalSize; }
}

class FileMetadataCache {
    private final String fileId;
    private final String fileName;
    private final long size;
    private final String contentType;
    private final String cdnUrl;
    private final long cachedAt;

    public FileMetadataCache(String fileId, String fileName, long size, 
                             String contentType, String cdnUrl) {
        this.fileId = fileId;
        this.fileName = fileName;
        this.size = size;
        this.contentType = contentType;
        this.cdnUrl = cdnUrl;
        this.cachedAt = System.currentTimeMillis();
    }

    public String getFileId() { return fileId; }
    public String getFileName() { return fileName; }
    public long getSize() { return size; }
    public String getContentType() { return contentType; }
    public String getCdnUrl() { return cdnUrl; }
    public long getCachedAt() { return cachedAt; }
}

class ChunkedUploadRequest {
    private final String fileName;
    private final long totalSize;
    private final String contentType;
    private final int chunkSizeBytes;
    private final String userId;
    private final String folderId;

    public ChunkedUploadRequest(String fileName, long totalSize, String contentType,
                                int chunkSizeBytes, String userId, String folderId) {
        this.fileName = fileName;
        this.totalSize = totalSize;
        this.contentType = contentType;
        this.chunkSizeBytes = chunkSizeBytes;
        this.userId = userId;
        this.folderId = folderId;
    }

    public String getFileName() { return fileName; }
    public long getTotalSize() { return totalSize; }
    public String getContentType() { return contentType; }
    public int getChunkSizeBytes() { return chunkSizeBytes; }
    public String getUserId() { return userId; }
    public String getFolderId() { return folderId; }
}

class DownloadResponse {
    private final String downloadUrl;
    private final long expiresAt;
    private final boolean isCdnUrl;
    private final Map<String, String> headers;

    public DownloadResponse(String downloadUrl, long expiresAt, 
                            boolean isCdnUrl, Map<String, String> headers) {
        this.downloadUrl = downloadUrl;
        this.expiresAt = expiresAt;
        this.isCdnUrl = isCdnUrl;
        this.headers = headers;
    }

    public String getDownloadUrl() { return downloadUrl; }
    public long getExpiresAt() { return expiresAt; }
    public boolean isCdnUrl() { return isCdnUrl; }
    public Map<String, String> getHeaders() { return headers; }
}

// ============================================================================
// Repository with Read Replica Support
// ============================================================================

interface FileMetadataRepository {
    FileMetadataCache save(FileMetadataCache metadata);
    FileMetadataCache findById(String fileId);
    List<FileMetadataCache> findByFolderId(String folderId);
    void delete(String fileId);
    
    // Read replica methods for read-heavy operations
    FileMetadataCache findByIdFromReplica(String fileId);
    List<FileMetadataCache> findByFolderIdFromReplica(String folderId);
}

// ============================================================================
// Cached File Storage Service
// ============================================================================

class CachedFileStorageService {
    private final FileMetadataRepository metadataRepository;
    private final Cache<String, FileMetadataCache> metadataCache;
    private final CDNService cdnService;
    private final ChunkManager chunkManager;
    
    // Cache TTL configurations
    private static final long METADATA_CACHE_TTL = 3600; // 1 hour
    private static final long DOWNLOAD_URL_EXPIRY = 3600; // 1 hour
    
    // Chunk size for large file uploads
    private static final int DEFAULT_CHUNK_SIZE = 5 * 1024 * 1024; // 5MB

    public CachedFileStorageService(FileMetadataRepository metadataRepository,
                                    Cache<String, FileMetadataCache> metadataCache,
                                    CDNService cdnService,
                                    ChunkManager chunkManager) {
        this.metadataRepository = metadataRepository;
        this.metadataCache = metadataCache;
        this.cdnService = cdnService;
        this.chunkManager = chunkManager;
    }

    /**
     * Get file metadata with caching.
     * Cache-aside pattern: check cache first, then DB.
     */
    public FileMetadataCache getFileMetadata(String fileId) {
        // Check cache first
        FileMetadataCache cached = metadataCache.get(fileId);
        if (cached != null) {
            return cached;
        }
        
        // Cache miss - read from replica (for read scaling)
        FileMetadataCache metadata = metadataRepository.findByIdFromReplica(fileId);
        if (metadata != null) {
            // Populate cache
            metadataCache.put(fileId, metadata, METADATA_CACHE_TTL);
        }
        
        return metadata;
    }

    /**
     * Initiate chunked upload for large files.
     * Returns upload session ID for resumable uploads.
     */
    public String initiateChunkedUpload(ChunkedUploadRequest request) {
        int chunkSize = request.getChunkSizeBytes() > 0 
            ? request.getChunkSizeBytes() 
            : DEFAULT_CHUNK_SIZE;
        
        // Create upload session
        String uploadId = chunkManager.initiateChunkedUpload(
            generateFileId(),
            request.getTotalSize(),
            chunkSize
        );
        
        return uploadId;
    }

    /**
     * Upload a single chunk.
     * Chunks can be uploaded in parallel and out of order.
     */
    public void uploadChunk(String uploadId, int chunkNumber, byte[] data) {
        chunkManager.uploadChunk(uploadId, chunkNumber, data);
    }

    /**
     * Get upload progress for resumable uploads.
     */
    public ChunkStatus getUploadProgress(String uploadId) {
        return chunkManager.getUploadStatus(uploadId);
    }

    /**
     * Complete chunked upload.
     * Assembles chunks and creates final file.
     */
    public FileMetadataCache completeChunkedUpload(String uploadId, 
                                                    String fileName,
                                                    String userId,
                                                    String folderId) {
        // Complete the upload (assemble chunks)
        chunkManager.completeChunkedUpload(uploadId);
        
        // Create metadata
        ChunkStatus status = chunkManager.getUploadStatus(uploadId);
        FileMetadataCache metadata = new FileMetadataCache(
            uploadId, // Using uploadId as fileId for simplicity
            fileName,
            status.getTotalSize(),
            detectContentType(fileName),
            null // CDN URL will be set on first download
        );
        
        // Save to database
        metadataRepository.save(metadata);
        
        // Cache the metadata
        metadataCache.put(metadata.getFileId(), metadata, METADATA_CACHE_TTL);
        
        return metadata;
    }

    /**
     * Get download URL - uses CDN for hot files.
     */
    public DownloadResponse getDownloadUrl(String fileId) {
        FileMetadataCache metadata = getFileMetadata(fileId);
        if (metadata == null) {
            throw new RuntimeException("File not found: " + fileId);
        }
        
        // Generate signed CDN URL
        String cdnUrl = cdnService.getSignedUrl(fileId, DOWNLOAD_URL_EXPIRY);
        
        return new DownloadResponse(
            cdnUrl,
            System.currentTimeMillis() + (DOWNLOAD_URL_EXPIRY * 1000),
            true,
            Map.of(
                "Content-Type", metadata.getContentType(),
                "Content-Disposition", "attachment; filename=\"" + metadata.getFileName() + "\""
            )
        );
    }

    /**
     * Delete file with cache invalidation.
     */
    public void deleteFile(String fileId, String userId) {
        // Invalidate caches first
        metadataCache.invalidate(fileId);
        cdnService.invalidateCache(fileId);
        
        // Delete from database (soft delete)
        metadataRepository.delete(fileId);
    }

    /**
     * List files in folder - uses read replica.
     */
    public List<FileMetadataCache> listFiles(String folderId) {
        // Use read replica for list operations
        return metadataRepository.findByFolderIdFromReplica(folderId);
    }

    // ========================================================================
    // Private Helpers
    // ========================================================================

    private String generateFileId() {
        // In production: use distributed ID generator
        return "file_" + System.currentTimeMillis() + "_" + 
               (int)(Math.random() * 10000);
    }

    private String detectContentType(String fileName) {
        // Simplified content type detection
        if (fileName.endsWith(".pdf")) return "application/pdf";
        if (fileName.endsWith(".jpg") || fileName.endsWith(".jpeg")) return "image/jpeg";
        if (fileName.endsWith(".png")) return "image/png";
        if (fileName.endsWith(".mp4")) return "video/mp4";
        if (fileName.endsWith(".txt")) return "text/plain";
        return "application/octet-stream";
    }
}

// ============================================================================
// Background Workers
// ============================================================================

class ThumbnailGenerationWorker {
    /**
     * Async worker that generates thumbnails for images/videos.
     * Triggered after file upload completion.
     */
    public CompletableFuture<String> generateThumbnail(String fileId) {
        return CompletableFuture.supplyAsync(() -> {
            // 1. Download original file
            // 2. Generate thumbnail
            // 3. Upload thumbnail to object storage
            // 4. Update metadata with thumbnail URL
            return "thumbnail_" + fileId;
        });
    }
}

class VirusScanWorker {
    /**
     * Async worker that scans uploaded files for viruses.
     * Runs before file is made publicly accessible.
     */
    public CompletableFuture<Boolean> scanFile(String fileId) {
        return CompletableFuture.supplyAsync(() -> {
            // 1. Download file
            // 2. Run virus scan
            // 3. Update file status (clean/quarantined)
            return true; // File is clean
        });
    }
}
