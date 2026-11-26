package iterator.v3;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.NoSuchElementException;

/**
 * v3-advanced: Paged Cursor-Based Streaming Iterator.
 * Translates batch paginated remote responses (e.g. REST/Database APIs with limit/cursor)
 * into a seamless, memory-bounded, item-by-item standard Java Iterator.
 */
public class PagedCursorIteratorDemo {

    public static class Page<T> {
        private final List<T> items;
        private final String nextCursor;

        public Page(List<T> items, String nextCursor) {
            this.items = new ArrayList<>(items);
            this.nextCursor = nextCursor;
        }

        public List<T> getItems() {
            return items;
        }

        public String getNextCursor() {
            return nextCursor;
        }

        public boolean hasNext() {
            return nextCursor != null && !nextCursor.isEmpty();
        }
    }

    @FunctionalInterface
    public interface PageFetcher<T> {
        Page<T> fetchPage(String cursor, int pageSize);
    }

    public static class PagedCursorIterator<T> implements Iterator<T> {
        private final PageFetcher<T> fetcher;
        private final int pageSize;
        private String currentCursor;
        private boolean isExhausted = false;

        private List<T> currentBuffer = new ArrayList<>();
        private int bufferIndex = 0;

        public PagedCursorIterator(PageFetcher<T> fetcher, int pageSize) {
            if (fetcher == null || pageSize <= 0) {
                throw new IllegalArgumentException("Invalid fetcher or page size");
            }
            this.fetcher = fetcher;
            this.pageSize = pageSize;
            this.currentCursor = null; // start from beginning
        }

        private void ensureBuffered() {
            if (bufferIndex < currentBuffer.size()) {
                return;
            }
            if (isExhausted) {
                return;
            }

            Page<T> page = fetcher.fetchPage(currentCursor, pageSize);
            if (page == null || page.getItems().isEmpty()) {
                isExhausted = true;
                return;
            }

            this.currentBuffer = page.getItems();
            this.bufferIndex = 0;
            this.currentCursor = page.getNextCursor();
            if (!page.hasNext()) {
                isExhausted = true;
            }
        }

        @Override
        public boolean hasNext() {
            ensureBuffered();
            return bufferIndex < currentBuffer.size();
        }

        @Override
        public T next() {
            if (!hasNext()) {
                throw new NoSuchElementException("No more items in paginated stream");
            }
            return currentBuffer.get(bufferIndex++);
        }
    }

    public static void main(String[] args) {
        PageFetcher<String> mockApi = (cursor, pageSize) -> {
            int start = cursor == null ? 0 : Integer.parseInt(cursor);
            if (start >= 10) {
                return new Page<>(List.of(), null);
            }
            int end = Math.min(start + pageSize, 10);
            List<String> items = new ArrayList<>();
            for (int i = start; i < end; i++) {
                items.add("Item-" + i);
            }
            String next = end < 10 ? String.valueOf(end) : null;
            return new Page<>(items, next);
        };

        PagedCursorIterator<String> stream = new PagedCursorIterator<>(mockApi, 3);
        while (stream.hasNext()) {
            System.out.println("Fetched: " + stream.next());
        }
    }
}
