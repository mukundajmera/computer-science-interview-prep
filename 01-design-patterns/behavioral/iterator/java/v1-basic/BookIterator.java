package iterator.v1;

import java.util.Arrays;
import java.util.NoSuchElementException;
import java.util.Objects;

/**
 * Forward iterator over a snapshot of book titles.
 *
 * <p>Time Complexity: O(n) snapshot copy on construction; O(1) per {@link #hasNext()}
 * and {@link #next()} call.
 * Space Complexity: O(n) for the defensive snapshot array.
 */
public class BookIterator implements Iterator<String> {

    private final String[] books;
    private int index;

    /**
     * Creates a forward iterator over all elements of the given array.
     *
     * @param books array of book titles to traverse
     */
    public BookIterator(String[] books) {
        this(books, Objects.requireNonNull(books, "books must not be null").length);
    }

    /**
     * Creates a forward iterator over the first {@code size} elements of the given array.
     *
     * @param books backing array of book titles
     * @param size  number of populated entries to traverse
     */
    public BookIterator(String[] books, int size) {
        Objects.requireNonNull(books, "books must not be null");
        if (size < 0 || size > books.length) {
            throw new IllegalArgumentException("Invalid size: " + size);
        }
        this.books = Arrays.copyOf(books, size);
        this.index = 0;
    }

    @Override
    public boolean hasNext() {
        return index < books.length;
    }

    @Override
    public String next() {
        if (!hasNext()) {
            throw new NoSuchElementException("No more books available");
        }
        return books[index++];
    }
}
