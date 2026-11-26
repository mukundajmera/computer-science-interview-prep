package v1_append;
import java.util.ArrayList;
import java.util.List;

public class AppendStore {
    public static class Point {
        public long ts;
        public double value;
        public Point(long ts, double value) { this.ts = ts; this.value = value; }
    }
    
    private List<Point> points = new ArrayList<>();
    
    public void append(long ts, double value) {
        if (!points.isEmpty() && ts < points.get(points.size()-1).ts) {
            throw new IllegalArgumentException("Out of order write");
        }
        points.add(new Point(ts, value));
    }
    
    public List<Point> rangeQuery(long start, long end) {
        List<Point> res = new ArrayList<>();
        for (Point p : points) {
            if (p.ts >= start && p.ts <= end) {
                res.add(p);
            }
        }
        return res;
    }
}
