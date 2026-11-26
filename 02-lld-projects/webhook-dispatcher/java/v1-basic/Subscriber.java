import java.util.regex.Pattern;

public class Subscriber {
    private final String id;
    private final String endpoint;
    private final String secret;
    private final Pattern topicRegex;

    public Subscriber(String id, String endpoint, String secret, String topicRegex) {
        this.id = id;
        this.endpoint = endpoint;
        this.secret = secret;
        this.topicRegex = Pattern.compile(topicRegex);
    }

    public String getId() { return id; }
    public String getEndpoint() { return endpoint; }
    public String getSecret() { return secret; }
    public Pattern getTopicRegex() { return topicRegex; }
}
