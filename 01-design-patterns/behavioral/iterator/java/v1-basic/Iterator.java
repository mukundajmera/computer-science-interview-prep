package iterator.v1;

/**
 * Custom Iterator interface for sequentially traversing a collection without
 * exposing its underlying representation.
 *
 * <p>Time Complexity: O(1) per {@link #hasNext()} and {@link #next()} call for
 * index-backed implementations.
 * Space Complexity: O(1) traversal cursor state.
 *
 * @param <T> the type of elements returned by this iterator
 */
public interface Iterator<T> {

    /**
     * Checks whether more elements remain to be visited.
     *
     * @return {@code true} if {@link #next()} can return another element
     */
    boolean hasNext();

    /**
     * Returns the next element in the traversal and advances the cursor.
     *
     * @return the next element
     * @throws java.util.NoSuchElementException if no elements remain
     */
    T next();
}
