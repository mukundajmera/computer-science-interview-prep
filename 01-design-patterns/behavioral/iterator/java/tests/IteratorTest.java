import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

import java.util.ArrayList;
import java.util.List;
import iterator.v1.*;
import iterator.v2.TreeIteratorDemo.*;
import iterator.v3.PagedCursorIteratorDemo.*;

public class IteratorTest {

    @Test
    @DisplayName("Forward BookIterator iterates collection items in order")
    void testForwardBookIteration() {
        BookCollection collection = new BookCollection(3);
        collection.addBook("Book 1");
        collection.addBook("Book 2");

        Iterator<String> it = collection.createIterator();
        assertTrue(it.hasNext());
        assertEquals("Book 1", it.next());
        assertTrue(it.hasNext());
        assertEquals("Book 2", it.next());
        assertFalse(it.hasNext());
    }

    @Test
    @DisplayName("ReverseBookIterator iterates items from last to first")
    void testReverseBookIteration() {
        String[] books = {"Alpha", "Beta", "Gamma"};
        Iterator<String> reverse = new ReverseBookIterator(books);

        assertTrue(reverse.hasNext());
        assertEquals("Gamma", reverse.next());
        assertTrue(reverse.hasNext());
        assertEquals("Beta", reverse.next());
        assertTrue(reverse.hasNext());
        assertEquals("Alpha", reverse.next());
        assertFalse(reverse.hasNext());
    }

    @Test
    @DisplayName("Empty collection iterator hasNext returns false immediately")
    void testEmptyCollectionIterator() {
        BookCollection emptyCollection = new BookCollection(2);
        Iterator<String> it = emptyCollection.createIterator();
        assertFalse(it.hasNext());
    }

    @Test
    @DisplayName("v2 TreeIterator produces DFS and BFS traversal orders")
    void testTreeIterators() {
        TreeNode root = new TreeNode("A");
        TreeNode b = new TreeNode("B");
        TreeNode c = new TreeNode("C");
        root.addChild(b).addChild(c);
        b.addChild(new TreeNode("D")).addChild(new TreeNode("E"));

        List<String> dfsList = new ArrayList<>();
        java.util.Iterator<TreeNode> dfs = root.dfsIterator();
        while (dfs.hasNext()) {
            dfsList.add(dfs.next().getName());
        }
        assertEquals(List.of("A", "B", "D", "E", "C"), dfsList);

        List<String> bfsList = new ArrayList<>();
        java.util.Iterator<TreeNode> bfs = root.bfsIterator();
        while (bfs.hasNext()) {
            bfsList.add(bfs.next().getName());
        }
        assertEquals(List.of("A", "B", "C", "D", "E"), bfsList);
    }

    @Test
    @DisplayName("v3 PagedCursorIterator seamlessly paginates batches across stream")
    void testPagedCursorIterator() {
        List<String> fullData = List.of("1", "2", "3", "4", "5");
        PageFetcher<String> fetcher = (cursor, pageSize) -> {
            int start = cursor == null ? 0 : Integer.parseInt(cursor);
            if (start >= fullData.size()) {
                return new Page<>(List.of(), null);
            }
            int end = Math.min(start + pageSize, fullData.size());
            String next = end < fullData.size() ? String.valueOf(end) : null;
            return new Page<>(fullData.subList(start, end), next);
        };

        PagedCursorIterator<String> it = new PagedCursorIterator<>(fetcher, 2);
        List<String> collected = new ArrayList<>();
        while (it.hasNext()) {
            collected.add(it.next());
        }
        assertEquals(fullData, collected);
    }
}
