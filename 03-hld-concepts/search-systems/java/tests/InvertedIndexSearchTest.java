import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class InvertedIndexSearchTest {

    private InvertedIndexSearch searchEngine;

    @BeforeEach
    public void setUp() {
        searchEngine = new InvertedIndexSearch();
    }

    @Test
    public void testSingleTermSearch() {
        searchEngine.addDocument(1, "The quick brown fox jumps over the lazy dog.");
        searchEngine.addDocument(2, "Fast foxes run quickly.");

        List<InvertedIndexSearch.SearchResult> results = searchEngine.search("fox", "OR");
        assertEquals(1, results.size());
        assertEquals(1, results.get(0).docId);
    }

    @Test
    public void testMultipleTermOrSearch() {
        searchEngine.addDocument(1, "The quick brown fox");
        searchEngine.addDocument(2, "The lazy dog");
        searchEngine.addDocument(3, "Quick brown dogs");

        List<InvertedIndexSearch.SearchResult> results = searchEngine.search("quick dog", "OR");
        assertEquals(3, results.size());

        boolean foundDoc1 = false;
        boolean foundDoc2 = false;
        boolean foundDoc3 = false;
        for (InvertedIndexSearch.SearchResult r : results) {
            if (r.docId == 1) foundDoc1 = true;
            if (r.docId == 2) foundDoc2 = true;
            if (r.docId == 3) foundDoc3 = true;
        }
        assertTrue(foundDoc1);
        assertTrue(foundDoc2);
        assertTrue(foundDoc3);
    }

    @Test
    public void testMultipleTermAndSearch() {
        searchEngine.addDocument(1, "The quick brown fox");
        searchEngine.addDocument(2, "The lazy dog");
        searchEngine.addDocument(3, "Quick brown dogs");

        List<InvertedIndexSearch.SearchResult> results = searchEngine.search("quick brown", "AND");
        assertEquals(2, results.size());

        boolean foundDoc1 = false;
        boolean foundDoc3 = false;
        for (InvertedIndexSearch.SearchResult r : results) {
            if (r.docId == 1) foundDoc1 = true;
            if (r.docId == 3) foundDoc3 = true;
        }
        assertTrue(foundDoc1);
        assertTrue(foundDoc3);
    }

    @Test
    public void testTfIdfScoringRanking() {
        searchEngine.addDocument(1, "Machine learning is a subset of AI. Machine learning is great.");
        searchEngine.addDocument(2, "Introduction to databases and machine systems.");
        searchEngine.addDocument(3, "Learning how to bake a cake.");

        List<InvertedIndexSearch.SearchResult> results = searchEngine.search("machine learning", "OR");

        assertEquals(3, results.size());
        // Doc 1 has two "machine" and two "learning" in a short doc, so it should rank highest.
        assertEquals(1, results.get(0).docId);

        // Doc 3 has "learning" and doc 2 has "machine".
        // They both have length 6.
        // Both terms "machine" and "learning" should have similar IDF.
        assertTrue(results.get(0).score > results.get(1).score);
    }
}
