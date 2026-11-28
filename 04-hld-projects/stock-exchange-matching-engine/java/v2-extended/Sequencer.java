package v2_extended;

import java.util.concurrent.atomic.AtomicLong;

public class Sequencer {
    private final AtomicLong sequence;

    public Sequencer() {
        this(0);
    }

    public Sequencer(long seed) {
        this.sequence = new AtomicLong(seed);
    }

    public long next() {
        return sequence.incrementAndGet();
    }
}
