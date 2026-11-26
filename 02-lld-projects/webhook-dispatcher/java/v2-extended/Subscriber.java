
import java.net.URI;
import java.net.URISyntaxException;
import java.util.regex.Pattern;

public class Subscriber {
    private final String id;
    private final String endpoint;
    private final String secret;
    private final Pattern topicRegex;
    private final String host;

    public Subscriber(String id, String endpoint, String secret, String topicRegex) {
        this.id = id;
        this.endpoint = endpoint;
        this.secret = secret;
        this.topicRegex = Pattern.compile(topicRegex);
        
        String extractedHost;
        try {
            extractedHost = new URI(endpoint).getHost();
            if (extractedHost == null) extractedHost = endpoint;
        } catch (URISyntaxException e) {
            extractedHost = endpoint;
        }
        this.host = extractedHost;
    }

    public String getId() { return id; }
    public String getEndpoint() { return endpoint; }
    public String getSecret() { return secret; }
    public Pattern getTopicRegex() { return topicRegex; }
    public String getHost() { return host; }
}
