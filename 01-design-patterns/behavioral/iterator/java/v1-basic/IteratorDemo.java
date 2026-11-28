package iterator.v1;

/**
 * Iterator Pattern - V1 Basic: Custom Collection.
 *
 * <p>Demonstrates forward, reverse, and keyword-filtered iteration over a
 * {@link BookCollection} without exposing its internal array storage.
 *
 * <p>Time Complexity: O(n) per full traversal of n books.
 * Space Complexity: O(n) for the collection and snapshot iterators.
 */
public class IteratorDemo {

    /**
     * Populates a sample book collection and prints forward, reverse, and filtered traversals.
     *
     * @param args unused command-line arguments
     */
    public static void main(String[] args) {
        BookCollection collection = new BookCollection();
        collection.addBook("Design Patterns");
        collection.addBook("Clean Code");
        collection.addBook("Refactoring");

        System.out.println("=== Forward Iteration ===");
        Iterator<String> forward = collection.createIterator();
        while (forward.hasNext()) {
            System.out.println(forward.next());
        }

        System.out.println("\n=== Reverse Iteration ===");
        Iterator<String> reverse = collection.createReverseIterator();
        while (reverse.hasNext()) {
            System.out.println(reverse.next());
        }

        System.out.println("\n=== Filtered Iteration ===");
        Iterator<String> filtered = collection.createFilteredIterator("code");
        while (filtered.hasNext()) {
            System.out.println(filtered.next());
        }
    }
}
