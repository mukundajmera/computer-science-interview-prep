package filestorage.v1;

/**
 * File Storage Service - V1 Basic
 * 
 * Core file storage service implementation.
 */

import java.time.Instant;
import java.util.*;

/**
 * File metadata entity.
 */
class FileMetadata {
    private final String fileId;
    private final String userId;
    private String filename;
    private final String contentType;
    private final long sizeBytes;
    private final String contentHash;
    private int version;
    private final Instant createdAt;
    private Instant updatedAt;
    private String parentFolderId;
    private boolean isFolder;
    private boolean isDeleted;
    
    public FileMetadata(String userId, String filename, String contentType,
                       long sizeBytes, String contentHash) {
        this.fileId = UUID.randomUUID().toString();
        this.userId = userId;
        this.filename = filename;
        this.contentType = contentType;
        this.sizeBytes = sizeBytes;
        this.contentHash = contentHash;
        this.version = 1;
        this.createdAt = Instant.now();
        this.updatedAt = Instant.now();
        this.isFolder = false;
        this.isDeleted = false;
    }
    
    // Getters
    public String getFileId() { return fileId; }
    public String getUserId() { return userId; }
    public String getFilename() { return filename; }
    public String getContentType() { return contentType; }
    public long getSizeBytes() { return sizeBytes; }
    public String getContentHash() { return contentHash; }
    public int getVersion() { return version; }
    public Instant getCreatedAt() { return createdAt; }
    public Instant getUpdatedAt() { return updatedAt; }
    public String getParentFolderId() { return parentFolderId; }
    public boolean isFolder() { return isFolder; }
    public boolean isDeleted() { return isDeleted; }
    
    public void setParentFolderId(String parentFolderId) {
        this.parentFolderId = parentFolderId;
        this.updatedAt = Instant.now();
    }
    
    public void incrementVersion() {
        this.version++;
        this.updatedAt = Instant.now();
    }
    
    public void markDeleted() {
        this.isDeleted = true;
        this.updatedAt = Instant.now();
    }
}

/**
 * File storage service interface.
 */
interface FileStorageService {
    /**
     * Upload a file.
     */
    FileMetadata upload(String userId, String filename, String contentType,
                       byte[] content);
    
    /**
     * Download a file.
     */
    byte[] download(String fileId, String userId);
    
    /**
     * Delete a file.
     */
    boolean delete(String fileId, String userId);
    
    /**
     * List files in a folder.
     */
    List<FileMetadata> listFiles(String userId, String folderId);
    
    /**
     * Get file metadata.
     */
    Optional<FileMetadata> getMetadata(String fileId);
}

/**
 * Block storage interface.
 */
interface BlockStorage {
    /**
     * Store a block of data.
     */
    String store(byte[] data);
    
    /**
     * Retrieve a block of data.
     */
    byte[] retrieve(String blockId);
    
    /**
     * Delete a block.
     */
    void delete(String blockId);
}

/**
 * Metadata repository interface.
 */
interface FileMetadataRepository {
    void save(FileMetadata metadata);
    Optional<FileMetadata> findById(String fileId);
    List<FileMetadata> findByUserAndParent(String userId, String parentFolderId);
    void delete(String fileId);
}

/**
 * Basic file storage service implementation.
 */
class BasicFileStorageService implements FileStorageService {
    
    private final FileMetadataRepository metadataRepository;
    private final BlockStorage blockStorage;
    
    public BasicFileStorageService(FileMetadataRepository metadataRepository,
                                   BlockStorage blockStorage) {
        this.metadataRepository = metadataRepository;
        this.blockStorage = blockStorage;
    }
    
    @Override
    public FileMetadata upload(String userId, String filename, String contentType,
                               byte[] content) {
        // Calculate content hash
        String contentHash = calculateHash(content);
        
        // Store content in block storage
        String blockId = blockStorage.store(content);
        
        // Create metadata
        FileMetadata metadata = new FileMetadata(
            userId, filename, contentType, content.length, contentHash);
        
        metadataRepository.save(metadata);
        
        return metadata;
    }
    
    @Override
    public byte[] download(String fileId, String userId) {
        FileMetadata metadata = metadataRepository.findById(fileId)
            .orElseThrow(() -> new FileNotFoundException("File not found: " + fileId));
        
        if (!metadata.getUserId().equals(userId)) {
            throw new AccessDeniedException("Access denied");
        }
        
        if (metadata.isDeleted()) {
            throw new FileNotFoundException("File has been deleted");
        }
        
        return blockStorage.retrieve(metadata.getContentHash());
    }
    
    @Override
    public boolean delete(String fileId, String userId) {
        Optional<FileMetadata> opt = metadataRepository.findById(fileId);
        
        if (opt.isEmpty()) {
            return false;
        }
        
        FileMetadata metadata = opt.get();
        if (!metadata.getUserId().equals(userId)) {
            throw new AccessDeniedException("Access denied");
        }
        
        metadata.markDeleted();
        metadataRepository.save(metadata);
        
        return true;
    }
    
    @Override
    public List<FileMetadata> listFiles(String userId, String folderId) {
        return metadataRepository.findByUserAndParent(userId, folderId);
    }
    
    @Override
    public Optional<FileMetadata> getMetadata(String fileId) {
        return metadataRepository.findById(fileId);
    }
    
    private String calculateHash(byte[] content) {
        try {
            java.security.MessageDigest digest = 
                java.security.MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(content);
            StringBuilder sb = new StringBuilder();
            for (byte b : hash) {
                sb.append(String.format("%02x", b));
            }
            return sb.toString();
        } catch (Exception e) {
            throw new RuntimeException("Failed to calculate hash", e);
        }
    }
}

/**
 * In-memory implementations.
 */
class InMemoryBlockStorage implements BlockStorage {
    private final Map<String, byte[]> storage = new HashMap<>();
    
    @Override
    public String store(byte[] data) {
        String blockId = UUID.randomUUID().toString();
        storage.put(blockId, data);
        return blockId;
    }
    
    @Override
    public byte[] retrieve(String blockId) {
        return storage.get(blockId);
    }
    
    @Override
    public void delete(String blockId) {
        storage.remove(blockId);
    }
}

class InMemoryFileMetadataRepository implements FileMetadataRepository {
    private final Map<String, FileMetadata> files = new HashMap<>();
    
    @Override
    public void save(FileMetadata metadata) {
        files.put(metadata.getFileId(), metadata);
    }
    
    @Override
    public Optional<FileMetadata> findById(String fileId) {
        return Optional.ofNullable(files.get(fileId));
    }
    
    @Override
    public List<FileMetadata> findByUserAndParent(String userId, String parentFolderId) {
        List<FileMetadata> result = new ArrayList<>();
        for (FileMetadata file : files.values()) {
            if (file.getUserId().equals(userId) && 
                !file.isDeleted() &&
                Objects.equals(file.getParentFolderId(), parentFolderId)) {
                result.add(file);
            }
        }
        return result;
    }
    
    @Override
    public void delete(String fileId) {
        files.remove(fileId);
    }
}

class FileNotFoundException extends RuntimeException {
    public FileNotFoundException(String message) { super(message); }
}

class AccessDeniedException extends RuntimeException {
    public AccessDeniedException(String message) { super(message); }
}
