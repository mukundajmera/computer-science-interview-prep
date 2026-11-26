import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class DocumentStoreEngineTest {
    private DocumentStoreEngine engine;
    private final String coll = "testColl";

    @BeforeEach
    public void setUp() {
        engine = new DocumentStoreEngine();
    }

    @Test
    public void testInsertAndSimpleQuery() {
        engine.insert(coll, new DocumentStoreEngine.Document().append("name", "Alice").append("age", 25));
        engine.insert(coll, new DocumentStoreEngine.Document().append("name", "Bob").append("age", 30));

        List<DocumentStoreEngine.Document> results = engine.find(coll, new DocumentStoreEngine.Document().append("name", "Alice"));
        assertEquals(1, results.size());
        assertEquals("Alice", results.get(0).get("name"));
        assertEquals(25, results.get(0).get("age"));
        assertNotNull(results.get(0).get("_id"));
    }

    @Test
    public void testQueryOperators() {
        engine.insert(coll, new DocumentStoreEngine.Document().append("name", "A").append("score", 10));
        engine.insert(coll, new DocumentStoreEngine.Document().append("name", "B").append("score", 20));
        engine.insert(coll, new DocumentStoreEngine.Document().append("name", "C").append("score", 30));

        // Test $gt
        List<DocumentStoreEngine.Document> gtResults = engine.find(coll, new DocumentStoreEngine.Document()
                .append("score", new DocumentStoreEngine.Document().append("$gt", 15)));
        assertEquals(2, gtResults.size());

        // Test $in
        List<DocumentStoreEngine.Document> inResults = engine.find(coll, new DocumentStoreEngine.Document()
                .append("name", new DocumentStoreEngine.Document().append("$in", Arrays.asList("A", "C"))));
        assertEquals(2, inResults.size());

        // Test $elemMatch
        engine.insert(coll, new DocumentStoreEngine.Document().append("name", "D")
                .append("tags", Arrays.asList(
                        new DocumentStoreEngine.Document().append("k", "v1"),
                        new DocumentStoreEngine.Document().append("k", "v2")
                )));

        List<DocumentStoreEngine.Document> elemMatchResults = engine.find(coll, new DocumentStoreEngine.Document()
                .append("tags", new DocumentStoreEngine.Document().append("$elemMatch", new DocumentStoreEngine.Document().append("k", "v2"))));
        assertEquals(1, elemMatchResults.size());
        assertEquals("D", elemMatchResults.get(0).get("name"));
    }

    @Test
    public void testProjection() {
        engine.insert(coll, new DocumentStoreEngine.Document().append("name", "Alice").append("age", 25).append("city", "NY"));

        // Inclusion projection
        List<DocumentStoreEngine.Document> resultsInclude = engine.find(coll,
                new DocumentStoreEngine.Document().append("name", "Alice"),
                new DocumentStoreEngine.Document().append("name", 1).append("_id", 0));
        assertEquals(1, resultsInclude.size());
        assertTrue(resultsInclude.get(0).containsKey("name"));
        assertFalse(resultsInclude.get(0).containsKey("age"));
        assertFalse(resultsInclude.get(0).containsKey("city"));
        assertFalse(resultsInclude.get(0).containsKey("_id")); // Explicitly excluded

        // Exclusion projection
        List<DocumentStoreEngine.Document> resultsExclude = engine.find(coll,
                new DocumentStoreEngine.Document().append("name", "Alice"),
                new DocumentStoreEngine.Document().append("age", 0));
        assertEquals(1, resultsExclude.size());
        assertTrue(resultsExclude.get(0).containsKey("name"));
        assertFalse(resultsExclude.get(0).containsKey("age"));
        assertTrue(resultsExclude.get(0).containsKey("city"));
        assertTrue(resultsExclude.get(0).containsKey("_id")); // Implicitly included
    }

    @Test
    public void testSecondaryIndex() {
        engine.createIndex(coll, "age");
        engine.insert(coll, new DocumentStoreEngine.Document().append("name", "A").append("age", 20));
        engine.insert(coll, new DocumentStoreEngine.Document().append("name", "B").append("age", 30));

        // Indexed query ($eq is implicit)
        List<DocumentStoreEngine.Document> results = engine.find(coll, new DocumentStoreEngine.Document().append("age", 30));
        assertEquals(1, results.size());
        assertEquals("B", results.get(0).get("name"));

        // Add a document after index creation
        engine.insert(coll, new DocumentStoreEngine.Document().append("name", "C").append("age", 30));
        List<DocumentStoreEngine.Document> resultsAfter = engine.find(coll, new DocumentStoreEngine.Document().append("age", 30));
        assertEquals(2, resultsAfter.size());
    }
}
