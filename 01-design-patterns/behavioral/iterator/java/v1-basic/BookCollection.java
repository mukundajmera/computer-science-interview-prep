package iterator.v1;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.Objects;

/**
 * Custom aggregate storing book titles and exposing forward, reverse, and filtered iterators.
 *
 * <p>Time Complexity: Amortized O(1) for {@link #addBook(String)}; O(n) to create
 * a snapshot-backed iterator.
 * Space Complexity: O(n) for storing n book titles.
 */
public class BookCollection {

    private static final int DEFAULT_CAPACITY = 16;

    private String[] books;
    private int size;

    /**
     * Creates an empty book collection with default initial capacity.
     */
    public BookCollection() {
        this(DEFAULT_CAPACITY);
    }

    /**
     * Creates an empty book collection with the specified initial capacity.
     *
     * @param capacity initial backing array capacity (must be non-negative)
     */
    public BookCollection(int capacity) {
        if (capacity < 0) {
            throw new IllegalArgumentException("Capacity must be non-negative: " + capacity);
        }
        this.books = new String[capacity];
        this.size = 0;
    }

    /**
     * Appends a book title to the collection, resizing the backing array when full.
     *
     * <p>Time Complexity: Amortized O(1). Space Complexity: O(1) amortized.
     *
     * @param book the book title to add
     */
    public void addBook(String book) {
        Objects.requireNonNull(book, "book must not be null");
        if (size == books.length) {
            int newCapacity = books.length == 0 ? DEFAULT_CAPACITY : books.length * 2;
            books = Arrays.copyOf(books, newCapacity);
        }
        books[size++] = book;
    }

    /**
     * Returns the number of books currently in the collection.
     *
     * @return current book count
     */
    public int size() {
        return size;
    }

    /**
     * Creates a forward iterator over a snapshot of the collection.
     *
     * @return a forward {@link Iterator} of book titles
     */
    public Iterator<String> createIterator() {
        return new BookIterator(books, size);
    }

    /**
     * Creates a reverse iterator over a snapshot of the collection.
     *
     * @return a reverse {@link Iterator} of book titles
     */
    public Iterator<String> createReverseIterator() {
        return new ReverseBookIterator(books, size);
    }

    /**
     * Creates an iterator yielding only book titles containing the keyword (case-insensitive).
     *
     * <p>Time Complexity: O(n * m) where n is the number of books and m is average title length.
     * Space Complexity: O(k) where k is the number of matching books.
     *
     * @param keyword substring to match case-insensitively
     * @return an {@link Iterator} over matching book titles
     */
    public Iterator<String> createFilteredIterator(String keyword) {
        Objects.requireNonNull(keyword, "keyword must not be null");
        String lowered = keyword.toLowerCase(Locale.ROOT);
        List<String> matches = new ArrayList<>();
        Iterator<String> forward = createIterator();
        while (forward.hasNext()) {
            String book = forward.next();
            if (book.toLowerCase(Locale.ROOT).contains(lowered)) {
                matches.add(book);
            }
        }
        return new BookIterator(matches.toArray(new String[0]));
    }
}
