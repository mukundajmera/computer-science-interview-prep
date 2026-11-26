import org.junit.jupiter.api.Test;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import static org.junit.jupiter.api.Assertions.*;

public class SimpleElasticsearchClientTest {

    @Test
    public void testSearchTextMatchesTitleAndBody() {
        SimpleElasticsearchClient client = new SimpleElasticsearchClient();

        Set<String> tags = new HashSet<>();
        tags.add("search");

        client.index(new SimpleElasticsearchClient.Document("1", "Search Engine Basics", "Intro to inverted indexes", tags));
        client.index(new SimpleElasticsearchClient.Document("2", "Advanced Topics", "More search capabilities", tags));
        client.index(new SimpleElasticsearchClient.Document("3", "Databases", "Relational db guide", new HashSet<>()));

        List<SimpleElasticsearchClient.Document> results1 = client.searchText("search");
        assertEquals(2, results1.size(), "Should find 'search' in title or body");

        List<SimpleElasticsearchClient.Document> results2 = client.searchText("inverted");
        assertEquals(1, results2.size(), "Should find 'inverted' in body");
        assertEquals("1", results2.get(0).id);
    }

    @Test
    public void testFilterByTag() {
        SimpleElasticsearchClient client = new SimpleElasticsearchClient();

        Set<String> tags1 = new HashSet<>();
        tags1.add("cache");

        Set<String> tags2 = new HashSet<>();
        tags2.add("search");
        tags2.add("distributed");

        client.index(new SimpleElasticsearchClient.Document("1", "Redis", "Cache", tags1));
        client.index(new SimpleElasticsearchClient.Document("2", "Elasticsearch", "Search", tags2));
        client.index(new SimpleElasticsearchClient.Document("3", "Solr", "Search", tags2));

        List<SimpleElasticsearchClient.Document> results = client.filterByTag("search");
        assertEquals(2, results.size(), "Should find 2 documents with 'search' tag");

        List<SimpleElasticsearchClient.Document> cacheResults = client.filterByTag("cache");
        assertEquals(1, cacheResults.size(), "Should find 1 document with 'cache' tag");
    }

    @Test
    public void testSearchReturnsEmptyWhenNoMatch() {
        SimpleElasticsearchClient client = new SimpleElasticsearchClient();

        client.index(new SimpleElasticsearchClient.Document("1", "Title", "Body", new HashSet<>()));

        List<SimpleElasticsearchClient.Document> textResults = client.searchText("MissingWord");
        assertTrue(textResults.isEmpty(), "Text search should return empty when no match");

        List<SimpleElasticsearchClient.Document> tagResults = client.filterByTag("missing_tag");
        assertTrue(tagResults.isEmpty(), "Tag filter should return empty when no match");
    }
}
