

import java.util.ArrayList;
import java.util.List;

public class GapBuffer {
    private String[] buffer;
    private int gapStart;
    private int gapEnd;
    private int capacity;

    public GapBuffer(int initialCapacity) {
        this.capacity = initialCapacity;
        this.buffer = new String[capacity];
        this.gapStart = 0;
        this.gapEnd = capacity;
    }

    private void resize() {
        int newCapacity = capacity * 2;
        String[] newBuffer = new String[newCapacity];

        // Copy elements before gap
        for (int i = 0; i < gapStart; i++) {
            newBuffer[i] = buffer[i];
        }

        // Copy elements after gap
        int elementsAfterGap = capacity - gapEnd;
        int newGapEnd = newCapacity - elementsAfterGap;
        for (int i = 0; i < elementsAfterGap; i++) {
            newBuffer[newGapEnd + i] = buffer[gapEnd + i];
        }

        this.buffer = newBuffer;
        this.gapEnd = newGapEnd;
        this.capacity = newCapacity;
    }

    private void moveGap(int index) {
        if (index < gapStart) {
            // Move gap left
            int shiftAmount = gapStart - index;
            for (int i = 0; i < shiftAmount; i++) {
                gapStart--;
                gapEnd--;
                buffer[gapEnd] = buffer[gapStart];
                buffer[gapStart] = null;
            }
        } else if (index > gapStart) {
            // Move gap right
            int shiftAmount = index - gapStart;
            for (int i = 0; i < shiftAmount; i++) {
                buffer[gapStart] = buffer[gapEnd];
                buffer[gapEnd] = null;
                gapStart++;
                gapEnd++;
            }
        }
    }

    public void insert(int index, String text) {
        if (gapStart == gapEnd) {
            resize();
        }

        int logicalLength = capacity - (gapEnd - gapStart);
        int actualIndex = Math.min(index, logicalLength);
        actualIndex = Math.max(0, actualIndex);

        moveGap(actualIndex);

        buffer[gapStart] = text;
        gapStart++;
    }

    public void delete(int index) {
        int logicalLength = capacity - (gapEnd - gapStart);
        if (index < 0 || index >= logicalLength) {
            return;
        }

        moveGap(index + 1);
        gapStart--;
        buffer[gapStart] = null;
    }

    public List<String> getAll() {
        List<String> result = new ArrayList<>();
        for (int i = 0; i < gapStart; i++) {
            result.add(buffer[i]);
        }
        for (int i = gapEnd; i < capacity; i++) {
            result.add(buffer[i]);
        }
        return result;
    }

    public void replace(int index, String text) {
        int logicalLength = capacity - (gapEnd - gapStart);
        if (index < 0 || index >= logicalLength) {
            return;
        }

        int physicalIndex;
        if (index < gapStart) {
            physicalIndex = index;
        } else {
            physicalIndex = index + (gapEnd - gapStart);
        }
        buffer[physicalIndex] = text;
    }
}
