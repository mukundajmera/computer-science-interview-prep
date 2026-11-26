

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.Arrays;

public class GapBufferTest {

    @Test
    public void testInsert() {
        GapBuffer gb = new GapBuffer(5);
        gb.insert(0, "Line 1");
        gb.insert(1, "Line 2");
        assertEquals(Arrays.asList("Line 1", "Line 2"), gb.getAll());
    }

    @Test
    public void testInsertMiddle() {
        GapBuffer gb = new GapBuffer(5);
        gb.insert(0, "Line 1");
        gb.insert(1, "Line 3");
        gb.insert(1, "Line 2"); // Insert between 1 and 3
        assertEquals(Arrays.asList("Line 1", "Line 2", "Line 3"), gb.getAll());
    }

    @Test
    public void testDelete() {
        GapBuffer gb = new GapBuffer(5);
        gb.insert(0, "A");
        gb.insert(1, "B");
        gb.insert(2, "C");
        gb.delete(1);
        assertEquals(Arrays.asList("A", "C"), gb.getAll());
    }

    @Test
    public void testReplace() {
        GapBuffer gb = new GapBuffer(5);
        gb.insert(0, "A");
        gb.insert(1, "B");
        gb.replace(1, "X");
        assertEquals(Arrays.asList("A", "X"), gb.getAll());
    }

    @Test
    public void testResize() {
        GapBuffer gb = new GapBuffer(2);
        gb.insert(0, "A");
        gb.insert(1, "B");
        gb.insert(2, "C"); // Trigger resize
        assertEquals(Arrays.asList("A", "B", "C"), gb.getAll());
    }
}
