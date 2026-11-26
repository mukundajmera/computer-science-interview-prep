package video.v3;

public interface DistributedVideoService {
    String resolveIngestRegion(String clientRegion);
    void replicateHotAsset(String videoId, String targetRegion);
    void rebuildManifestIndex(String region);
}
