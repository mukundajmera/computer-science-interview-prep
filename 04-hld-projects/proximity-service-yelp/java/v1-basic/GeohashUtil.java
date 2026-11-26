import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class GeohashUtil {
    private static final String BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz";
    private static final double EARTH_RADIUS_KM = 6371.0;

    public static String encode(double lat, double lon, int precision) {
        double[] latInterval = {-90.0, 90.0};
        double[] lonInterval = {-180.0, 180.0};
        StringBuilder geohash = new StringBuilder();
        int[] bits = {16, 8, 4, 2, 1};
        int bit = 0;
        int ch = 0;
        boolean even = true;

        while (geohash.length() < precision) {
            if (even) {
                double mid = (lonInterval[0] + lonInterval[1]) / 2.0;
                if (lon >= mid) {
                    ch |= bits[bit];
                    lonInterval[0] = mid;
                } else {
                    lonInterval[1] = mid;
                }
            } else {
                double mid = (latInterval[0] + latInterval[1]) / 2.0;
                if (lat >= mid) {
                    ch |= bits[bit];
                    latInterval[0] = mid;
                } else {
                    latInterval[1] = mid;
                }
            }

            even = !even;
            if (bit < 4) {
                bit++;
            } else {
                geohash.append(BASE32.charAt(ch));
                bit = 0;
                ch = 0;
            }
        }

        return geohash.toString();
    }

    public static double[] decode(String geohash) {
        double[] latInterval = {-90.0, 90.0};
        double[] lonInterval = {-180.0, 180.0};
        boolean even = true;
        int[] bits = {16, 8, 4, 2, 1};

        for (int i = 0; i < geohash.length(); i++) {
            char c = geohash.charAt(i);
            int val = BASE32.indexOf(c);
            for (int bit : bits) {
                if (even) {
                    double mid = (lonInterval[0] + lonInterval[1]) / 2.0;
                    if ((val & bit) != 0) {
                        lonInterval[0] = mid;
                    } else {
                        lonInterval[1] = mid;
                    }
                } else {
                    double mid = (latInterval[0] + latInterval[1]) / 2.0;
                    if ((val & bit) != 0) {
                        latInterval[0] = mid;
                    } else {
                        latInterval[1] = mid;
                    }
                }
                even = !even;
            }
        }

        double lat = (latInterval[0] + latInterval[1]) / 2.0;
        double lon = (lonInterval[0] + lonInterval[1]) / 2.0;
        return new double[]{lat, lon};
    }

    public static double[] getDimensions(int precision) {
        double latDim = 180.0;
        double lonDim = 360.0;
        for (int i = 0; i < precision * 5; i++) {
            if (i % 2 == 0) {
                lonDim /= 2.0;
            } else {
                latDim /= 2.0;
            }
        }
        return new double[]{latDim, lonDim};
    }

    public static List<String> getNeighbors(String geohash) {
        if (geohash == null || geohash.isEmpty()) {
            return new ArrayList<>();
        }

        double[] coords = decode(geohash);
        double lat = coords[0];
        double lon = coords[1];

        double[] dims = getDimensions(geohash.length());
        double latDim = dims[0];
        double lonDim = dims[1];

        Set<String> neighbors = new HashSet<>();
        double[] dLats = {-latDim, 0.0, latDim};
        double[] dLons = {-lonDim, 0.0, lonDim};

        for (double dlat : dLats) {
            for (double dlon : dLons) {
                if (dlat == 0.0 && dlon == 0.0) {
                    continue;
                }

                double nlat = lat + dlat;
                double nlon = lon + dlon;

                if (nlat > 90.0 || nlat < -90.0) {
                    continue;
                }
                if (nlon > 180.0) {
                    nlon -= 360.0;
                } else if (nlon < -180.0) {
                    nlon += 360.0;
                }

                neighbors.add(encode(nlat, nlon, geohash.length()));
            }
        }

        return new ArrayList<>(neighbors);
    }

    public static double haversineDistance(double lat1, double lon1, double lat2, double lon2) {
        double dLat = Math.toRadians(lat2 - lat1);
        double dLon = Math.toRadians(lon2 - lon1);

        double a = Math.pow(Math.sin(dLat / 2.0), 2) +
                   Math.cos(Math.toRadians(lat1)) * Math.cos(Math.toRadians(lat2)) *
                   Math.pow(Math.sin(dLon / 2.0), 2);
        a = Math.max(0.0, Math.min(1.0, a));
        double c = 2.0 * Math.atan2(Math.sqrt(a), Math.sqrt(1.0 - a));

        return EARTH_RADIUS_KM * c;
    }
}