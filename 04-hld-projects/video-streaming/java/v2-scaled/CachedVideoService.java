package video.v2;

interface ProcessingOrchestrator {
    void enqueueVariantJobs(String videoId);
    void markVariantReady(String videoId, String variant);
    void markFailed(String videoId, String reason);
}

interface UploadPartRegistry {
    void recordPart(String sessionId, int partNumber, String etag);
    boolean hasAllParts(String sessionId, int expectedParts);
}

interface ManifestReadinessStore {
    String getState(String videoId);
    void setState(String videoId, String state);
}
