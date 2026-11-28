/**
 * v2 Business: v1 fields plus category, rating and open_now attributes
 * (improvement #2, FOLLOW-UPS.md #4). The 3-arg constructor preserves
 * v1 call sites. See ProximityServiceV2 for the full v2 list.
 */
public class BusinessV2 {
    private final String id;
    private final double lat;
    private final double lon;
    private final String category;
    private final double rating;
    private final boolean openNow;

    public BusinessV2(String id, double lat, double lon) {
        this(id, lat, lon, "", 0.0, true);
    }

    public BusinessV2(String id, double lat, double lon, String category, double rating, boolean openNow) {
        this.id = id;
        this.lat = lat;
        this.lon = lon;
        this.category = category;
        this.rating = rating;
        this.openNow = openNow;
    }

    public String getId() {
        return id;
    }

    public double getLat() {
        return lat;
    }

    public double getLon() {
        return lon;
    }

    public String getCategory() {
        return category;
    }

    public double getRating() {
        return rating;
    }

    public boolean isOpenNow() {
        return openNow;
    }
}
