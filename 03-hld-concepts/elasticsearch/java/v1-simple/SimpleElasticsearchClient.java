import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * Interview-scale in-memory search client with lightweight filtering.
 */
public class SimpleElasticsearchClient {
    public static final class Document {
        public final String id;
        public final String title;
        public final String body;
        public final Set<String> tags;

        public Document(String id, String title, String body, Set<String> tags) {
            this.id = id;
            this.title = title;
            this.body = body;
            this.tags = tags == null ? new HashSet<>() : tags;
        }
    }

    private final List<Document> documents = new ArrayList<>();

    public void index(Document document) {
        documents.add(document);
    }

    public List<Document> searchText(String query) {
        List<Document> results = new ArrayList<>();
        String needle = query.toLowerCase();
        for (Document document : documents) {
            if (document.title.toLowerCase().contains(needle)
                || document.body.toLowerCase().contains(needle)) {
                results.add(document);
            }
        }
        return results;
    }

    public List<Document> filterByTag(String tag) {
        List<Document> results = new ArrayList<>();
        for (Document document : documents) {
            if (document.tags.contains(tag)) {
                results.add(document);
            }
        }
        return results;
    }

    public static void main(String[] args) {
        SimpleElasticsearchClient client = new SimpleElasticsearchClient();
        Set<String> distributed = new HashSet<>();
        distributed.add("distributed");
        distributed.add("search");

        client.index(new Document("1", "Design Search", "Elasticsearch basics", distributed));
        client.index(new Document("2", "Cache Guide", "Redis cache-aside pattern", new HashSet<>()));

        System.out.println("searchText('search') -> " + client.searchText("search").size());
        System.out.println("filterByTag('distributed') -> " + client.filterByTag("distributed").size());
    }
}
