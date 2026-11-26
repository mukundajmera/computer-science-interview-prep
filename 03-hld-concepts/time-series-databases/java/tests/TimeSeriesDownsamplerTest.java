import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class TimeSeriesDownsamplerTest {

    private TimeSeriesDownsampler tsdb;

    @BeforeEach
    public void setUp() {
        tsdb = new TimeSeriesDownsampler();
    }

    @Test
    public void testInsertAndRangeQuery() {
        Map<String, String> tags1 = new HashMap<>();
        tags1.put("host", "server1");

        Map<String, String> tags2 = new HashMap<>();
        tags2.put("host", "server2");

        tsdb.insert(new TimeSeriesDownsampler.DataPoint("cpu", 1000, 45.0, tags1));
        tsdb.insert(new TimeSeriesDownsampler.DataPoint("cpu", 2000, 50.0, tags1));
        tsdb.insert(new TimeSeriesDownsampler.DataPoint("cpu", 3000, 55.0, tags2));

        // Range query without tags
        List<TimeSeriesDownsampler.DataPoint> results = tsdb.rangeQuery("cpu", 1000, 2500, null);
        assertEquals(2, results.size());
        assertEquals(45.0, results.get(0).getValue(), 0.001);
        assertEquals(50.0, results.get(1).getValue(), 0.001);

        // Range query with tags
        Map<String, String> queryTags = new HashMap<>();
        queryTags.put("host", "server2");
        List<TimeSeriesDownsampler.DataPoint> resultsTags = tsdb.rangeQuery("cpu", 1000, 3000, queryTags);
        assertEquals(1, resultsTags.size());
        assertEquals(55.0, resultsTags.get(0).getValue(), 0.001);
    }

    @Test
    public void testDownsampleAvg() {
        tsdb.insert(new TimeSeriesDownsampler.DataPoint("memory", 60, 10.0, null));
        tsdb.insert(new TimeSeriesDownsampler.DataPoint("memory", 90, 20.0, null)); // bucket 60
        tsdb.insert(new TimeSeriesDownsampler.DataPoint("memory", 120, 30.0, null));
        tsdb.insert(new TimeSeriesDownsampler.DataPoint("memory", 150, 40.0, null)); // bucket 120

        List<TimeSeriesDownsampler.DataPoint> results = tsdb.downsample("memory", 60, TimeSeriesDownsampler.AggregationType.AVG);

        assertEquals(2, results.size());
        assertEquals(60, results.get(0).getTimestamp());
        assertEquals(15.0, results.get(0).getValue(), 0.001); // (10+20)/2

        assertEquals(120, results.get(1).getTimestamp());
        assertEquals(35.0, results.get(1).getValue(), 0.001); // (30+40)/2
    }

    @Test
    public void testDownsampleMinMaxSum() {
        tsdb.insert(new TimeSeriesDownsampler.DataPoint("req", 10, 5.0, null));
        tsdb.insert(new TimeSeriesDownsampler.DataPoint("req", 20, 10.0, null));
        tsdb.insert(new TimeSeriesDownsampler.DataPoint("req", 30, 2.0, null));
        tsdb.insert(new TimeSeriesDownsampler.DataPoint("req", 40, 8.0, null));

        // All in bucket 0
        List<TimeSeriesDownsampler.DataPoint> minRes = tsdb.downsample("req", 100, TimeSeriesDownsampler.AggregationType.MIN);
        assertEquals(1, minRes.size());
        assertEquals(2.0, minRes.get(0).getValue(), 0.001);

        List<TimeSeriesDownsampler.DataPoint> maxRes = tsdb.downsample("req", 100, TimeSeriesDownsampler.AggregationType.MAX);
        assertEquals(1, maxRes.size());
        assertEquals(10.0, maxRes.get(0).getValue(), 0.001);

        List<TimeSeriesDownsampler.DataPoint> sumRes = tsdb.downsample("req", 100, TimeSeriesDownsampler.AggregationType.SUM);
        assertEquals(1, sumRes.size());
        assertEquals(25.0, sumRes.get(0).getValue(), 0.001);
    }

    @Test
    public void testApplyRetention() {
        tsdb.insert(new TimeSeriesDownsampler.DataPoint("temp", 1000, 20.0, null));
        tsdb.insert(new TimeSeriesDownsampler.DataPoint("temp", 2000, 22.0, null));
        tsdb.insert(new TimeSeriesDownsampler.DataPoint("temp", 3000, 21.0, null));

        // current time 3500, retention 1000. Cutoff is 2500
        tsdb.applyRetention(3500, 1000);

        List<TimeSeriesDownsampler.DataPoint> results = tsdb.rangeQuery("temp", 0, 5000, null);
        assertEquals(1, results.size());
        assertEquals(3000, results.get(0).getTimestamp());
        assertEquals(21.0, results.get(0).getValue(), 0.001);
    }
}
