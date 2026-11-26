package v1_basic.multi_region;

public class Record {
    private String id;
    private String data;
    private HybridLogicalClock hlc;
    private String originRegion;
    private boolean tombstone;

    public Record(String id, String data, HybridLogicalClock hlc, String originRegion, boolean tombstone) {
        this.id = id;
        this.data = data;
        this.hlc = hlc;
        this.originRegion = originRegion;
        this.tombstone = tombstone;
    }

    public String getId() { return id; }
    public String getData() { return data; }
    public HybridLogicalClock getHlc() { return hlc; }
    public String getOriginRegion() { return originRegion; }
    public boolean isTombstone() { return tombstone; }
}
