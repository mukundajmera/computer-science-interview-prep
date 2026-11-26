import java.util.List;

public class Demo {
    public static void main(String[] args) {
        InvertedIndexSearch searchEngine = new InvertedIndexSearch();

        searchEngine.addDocument(1, "The quick brown fox jumps over the lazy dog.");
        searchEngine.addDocument(2, "Fast foxes run quickly.");
        searchEngine.addDocument(3, "Quick brown dogs.");

        System.out.println("Search 'quick':");
        List<InvertedIndexSearch.SearchResult> results = searchEngine.search("quick", "OR");
        for (InvertedIndexSearch.SearchResult result : results) {
            System.out.println("Doc " + result.docId + ", Score: " + result.score);
        }

        System.out.println("\nSearch 'quick brown' (AND):");
        results = searchEngine.search("quick brown", "AND");
        for (InvertedIndexSearch.SearchResult result : results) {
            System.out.println("Doc " + result.docId + ", Score: " + result.score);
        }
    }
}
