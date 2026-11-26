public class Snowflake {
    private long workerId;
    private long sequence = 0;
    private long lastTimestamp = -1;

    public Snowflake(long workerId) {
        this.workerId = workerId;
    }

    public synchronized long nextId() throws Exception {
        long timestamp = System.currentTimeMillis();
        if (timestamp < lastTimestamp) {
            throw new Exception("Clock moved backwards");
        }
        if (timestamp == lastTimestamp) {
            sequence = (sequence + 1) & 4095;
            if (sequence == 0) {
                while (timestamp <= lastTimestamp) {
                    timestamp = System.currentTimeMillis();
                }
            }
        } else {
            sequence = 0;
        }
        lastTimestamp = timestamp;
        return (timestamp << 22) | (workerId << 12) | sequence;
    }

    public static void main(String[] args) throws Exception {
        Snowflake s = new Snowflake(1);
        long prev = -1;
        
        // Test 1-5: Monotonic
        for (int i = 0; i < 5; i++) {
            long curr = s.nextId();
            assert curr > prev;
            prev = curr;
        }

        // Test 6: clock regression
        Snowflake s2 = new Snowflake(1);
        s2.lastTimestamp = System.currentTimeMillis() + 10000;
        boolean threw = false;
        try {
            s2.nextId();
        } catch (Exception e) {
            threw = true;
        }
        assert threw;
    }
}
