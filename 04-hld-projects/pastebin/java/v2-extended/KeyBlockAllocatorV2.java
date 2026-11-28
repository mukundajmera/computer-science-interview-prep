import java.util.ArrayList;
import java.util.List;

/**
 * v2 improvement #3 (FOLLOW-UPS.md #3): KGS-style key block allocation.
 * Short-link ids are handed out from pre-allocated blocks, the way a Key
 * Generation Service pre-generates keys, instead of a bare shared
 * counter. Exhaustion is loud and explicit instead of a silent
 * collision.
 */
public class KeyBlockAllocatorV2 {
    private long nextBlockStart;
    private final int blockSize;
    private final Integer maxBlocks; // null means unlimited
    private int blocksAllocated = 0;
    private List<Long> currentBlock = new ArrayList<>();
    private int index = 0;

    public KeyBlockAllocatorV2(long startId, int blockSize, Integer maxBlocks) {
        if (blockSize <= 0) {
            throw new IllegalArgumentException("blockSize must be positive");
        }
        this.nextBlockStart = startId;
        this.blockSize = blockSize;
        this.maxBlocks = maxBlocks;
    }

    public KeyBlockAllocatorV2() {
        this(1000000000L, 1000, null);
    }

    public synchronized long nextId() {
        if (index >= currentBlock.size()) {
            if (maxBlocks != null && blocksAllocated >= maxBlocks) {
                throw new IllegalStateException("KeyPoolExhausted: no free key blocks left");
            }
            currentBlock = new ArrayList<>(blockSize);
            for (int i = 0; i < blockSize; i++) {
                currentBlock.add(nextBlockStart + i);
            }
            nextBlockStart += blockSize;
            blocksAllocated++;
            index = 0;
        }
        return currentBlock.get(index++);
    }

    public synchronized int getBlocksAllocated() {
        return blocksAllocated;
    }
}
