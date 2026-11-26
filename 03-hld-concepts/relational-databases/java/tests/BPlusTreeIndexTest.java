package tests;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import v1_simple.BPlusTreeIndex;

import java.util.List;

public class BPlusTreeIndexTest {

    @Test
    public void testInsertAndSearch() {
        BPlusTreeIndex<Integer, String> tree = new BPlusTreeIndex<>(4);
        tree.insert(10, "A");
        tree.insert(20, "B");
        tree.insert(5, "C");

        assertEquals("A", tree.search(10));
        assertEquals("B", tree.search(20));
        assertEquals("C", tree.search(5));
        assertNull(tree.search(15));
    }

    @Test
    public void testUpdateExistingKey() {
        BPlusTreeIndex<Integer, String> tree = new BPlusTreeIndex<>(3);
        tree.insert(1, "Old");
        tree.insert(1, "New");

        assertEquals("New", tree.search(1));
    }

    @Test
    public void testNodeSplit() {
        BPlusTreeIndex<Integer, String> tree = new BPlusTreeIndex<>(3);
        for (int i = 1; i <= 10; i++) {
            tree.insert(i, "Val_" + i);
        }

        for (int i = 1; i <= 10; i++) {
            assertEquals("Val_" + i, tree.search(i));
        }
    }

    @Test
    public void testRangeScan() {
        BPlusTreeIndex<Integer, String> tree = new BPlusTreeIndex<>(4);
        tree.insert(10, "A");
        tree.insert(20, "B");
        tree.insert(30, "C");
        tree.insert(40, "D");
        tree.insert(50, "E");

        List<BPlusTreeIndex.Entry<Integer, String>> results = tree.rangeScan(20, 45);
        assertEquals(3, results.size());
        assertEquals(new BPlusTreeIndex.Entry<>(20, "B"), results.get(0));
        assertEquals(new BPlusTreeIndex.Entry<>(30, "C"), results.get(1));
        assertEquals(new BPlusTreeIndex.Entry<>(40, "D"), results.get(2));
    }

    @Test
    public void testRangeScanEmpty() {
        BPlusTreeIndex<Integer, String> tree = new BPlusTreeIndex<>(4);
        tree.insert(10, "A");
        tree.insert(20, "B");

        List<BPlusTreeIndex.Entry<Integer, String>> results = tree.rangeScan(30, 50);
        assertTrue(results.isEmpty());
    }
}
