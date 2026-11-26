package v1_basic;

import java.util.concurrent.atomic.AtomicLong;

public class Sequencer {
    private final AtomicLong sequence = new AtomicLong(0);

    public long next() {
        return sequence.incrementAndGet();
    }
}