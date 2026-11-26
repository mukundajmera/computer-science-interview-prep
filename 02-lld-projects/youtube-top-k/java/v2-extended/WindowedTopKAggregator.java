public interface WindowedTopKAggregator {
    void ingest(String videoId, long eventTimeMs);
}
