package tests;
import v1_append.AppendStore;
import v2_compression.GorillaCompression;
import v3_blocks.TsdbEngine;

import java.util.List;

public class TsdbTests {
    public static void main(String[] args) {
        testAppend();
        testGorilla();
        testTsdb();
        System.out.println("All tests passed!");
    }
    
    static void testAppend() {
        AppendStore s = new AppendStore();
        s.append(100, 1.0);
        s.append(200, 2.0);
        assert s.rangeQuery(150, 250).size() == 1;
    }
    
    static void testGorilla() {
        GorillaCompression.Compressor c = new GorillaCompression.Compressor();
        long[] timestamps = {1600000000L, 1600000015L, 1600000030L, 1600000046L, 1600000060L, 1600000075L};
        for (long t : timestamps) {
            c.addTimestamp(t);
        }
        
        GorillaCompression.Decompressor d = new GorillaCompression.Decompressor(c.writer.bits);
        List<Long> res = d.readTimestamps(timestamps.length);
        for (int i = 0; i < timestamps.length; i++) {
            if (res.get(i) != timestamps[i]) {
                throw new RuntimeException("Mismatch at " + i + ": " + res.get(i) + " vs " + timestamps[i]);
            }
        }
    }
    
    static void testTsdb() {
        TsdbEngine db = new TsdbEngine(2);
        db.insert("cpu", 10, 1.0);
        db.insert("cpu", 15, 2.0);
        db.insert("cpu", 25, 3.0);
        
        List<TsdbEngine.Point> res = db.downsample("cpu", 20);
        assert res.size() == 2;
        assert res.get(0).value == 1.5;
        assert res.get(1).value == 3.0;
        
        db.insert("mem", 10, 1.0);
        try {
            db.insert("disk", 10, 1.0);
            throw new RuntimeException("Should have thrown");
        } catch (IllegalStateException e) {
            // OK
        }
        
        db.applyRetention(15);
        assert db.rangeQuery("cpu", 0, 100).size() == 2;
    }
}
