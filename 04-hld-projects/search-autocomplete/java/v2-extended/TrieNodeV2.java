import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * v2 trie node. v1 uses the default package, so v2 classes carry the V2
 * suffix to compile side by side; structure and behavior are unchanged.
 */
public class TrieNodeV2 {
    private final Map<Character, TrieNodeV2> children;
    private boolean isTerminal;
    private long frequency;
    private List<Suggestion> topSuggestions;

    public TrieNodeV2() {
        this.children = new HashMap<>();
        this.isTerminal = false;
        this.frequency = 0;
        this.topSuggestions = new ArrayList<>();
    }

    public Map<Character, TrieNodeV2> getChildren() {
        return children;
    }

    public boolean isTerminal() {
        return isTerminal;
    }

    public void setTerminal(boolean terminal) {
        isTerminal = terminal;
    }

    public long getFrequency() {
        return frequency;
    }

    public void setFrequency(long frequency) {
        this.frequency = frequency;
    }

    public List<Suggestion> getTopSuggestions() {
        return topSuggestions;
    }

    public void setTopSuggestions(List<Suggestion> topSuggestions) {
        this.topSuggestions = topSuggestions;
    }

    public static class Suggestion {
        private final String query;
        private final long frequency;

        public Suggestion(String query, long frequency) {
            this.query = query;
            this.frequency = frequency;
        }

        public String getQuery() {
            return query;
        }

        public long getFrequency() {
            return frequency;
        }

        @Override
        public String toString() {
            return "Suggestion{" +
                    "query='" + query + '\'' +
                    ", frequency=" + frequency +
                    '}';
        }
    }
}
