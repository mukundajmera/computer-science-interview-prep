import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Demo {
    public static void main(String[] args) {
        TimeSeriesDownsampler tsdb = new TimeSeriesDownsampler();

        // Insert
        Map<String, String> tags1 = new HashMap<>();
        tags1.put("host", "serverA");
        tsdb.insert(new TimeSeriesDownsampler.DataPoint("cpu_utilization", 100, 45.5, tags1));
        tsdb.insert(new TimeSeriesDownsampler.DataPoint("cpu_utilization", 200, 50.0, tags1));
        tsdb.insert(new TimeSeriesDownsampler.DataPoint("cpu_utilization", 300, 60.5, tags1));

        // Range query
        System.out.println("Range Query [0, 250]:");
        List<TimeSeriesDownsampler.DataPoint> results = tsdb.rangeQuery("cpu_utilization", 0, 250, null);
        for (TimeSeriesDownsampler.DataPoint p : results) {
            System.out.println(p);
        }

        // Downsample
        System.out.println("\nDownsample with AVG (bucket size 300):");
        List<TimeSeriesDownsampler.DataPoint> downsampled = tsdb.downsample("cpu_utilization", 300, TimeSeriesDownsampler.AggregationType.AVG);
        for (TimeSeriesDownsampler.DataPoint p : downsampled) {
            System.out.println(p);
        }

        // Apply retention
        System.out.println("\nApplying retention (current time 500, period 250)...");
        tsdb.applyRetention(500, 250);
        List<TimeSeriesDownsampler.DataPoint> retained = tsdb.rangeQuery("cpu_utilization", 0, 1000, null);
        for (TimeSeriesDownsampler.DataPoint p : retained) {
            System.out.println(p);
        }
    }
}
