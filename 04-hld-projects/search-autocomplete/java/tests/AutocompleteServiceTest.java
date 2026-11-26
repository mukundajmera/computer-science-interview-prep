import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.*;

import static org.junit.jupiter.api.Assertions.*;

public class AutocompleteServiceTest {

    private Set<String> profanityBlacklist;

    @BeforeEach
    public void setUp() {
        profanityBlacklist = new HashSet<>(Arrays.asList("badword", "profane"));
    }

    @Test
    public void testTop5SuggestionsRankedByFrequency() {
        AutocompleteService service = new AutocompleteService(profanityBlacklist);
        QueryAggregator aggregator = new QueryAggregator();
        
        aggregator.addQuery("apple");
        aggregator.addQuery("apple");
        aggregator.addQuery("apple"); // 3
        
        aggregator.addQuery("app");
        aggregator.addQuery("app");
        aggregator.addQuery("app");
        aggregator.addQuery("app"); // 4
        
        aggregator.addQuery("application");
        aggregator.addQuery("application"); // 2
        
        aggregator.addQuery("append"); // 1
        
        aggregator.addQuery("appreciate"); // 1
        
        aggregator.addQuery("apply"); // 1
        
        aggregator.addQuery("apt"); // 1 (different prefix)
        
        // We have 6 queries starting with "app"
        // Frequencies:
        // app: 4
        // apple: 3
        // application: 2
        // append: 1
        // appreciate: 1
        // apply: 1
        
        // Top 5 for "app" should be: app, apple, application, and 2 of (append, appreciate, apply)
        service.rebuildTrie(aggregator.getAggregatedFrequencies());
        
        List<String> suggestions = service.getSuggestions("app");
        assertEquals(5, suggestions.size());
        assertEquals("app", suggestions.get(0));
        assertEquals("apple", suggestions.get(1));
        assertEquals("application", suggestions.get(2));
    }

    @Test
    public void testPrefixLengthCapping() {
        AutocompleteService service = new AutocompleteService(profanityBlacklist);
        Map<String, Long> frequencies = new HashMap<>();
        
        String longPrefix = "a".repeat(50);
        String veryLongQuery = "a".repeat(60);
        frequencies.put(veryLongQuery, 10L);
        
        service.rebuildTrie(frequencies);
        
        List<String> suggestions = service.getSuggestions(longPrefix);
        assertEquals(1, suggestions.size());
        assertEquals(veryLongQuery, suggestions.get(0));
        
        // Capped query
        List<String> suggestionsOverLimit = service.getSuggestions("a".repeat(70));
        assertEquals(1, suggestionsOverLimit.size());
        assertEquals(veryLongQuery, suggestionsOverLimit.get(0));
    }

    @Test
    public void testProfanityBlacklistFiltering() {
        AutocompleteService service = new AutocompleteService(profanityBlacklist);
        Map<String, Long> frequencies = new HashMap<>();
        
        frequencies.put("goodword", 10L);
        frequencies.put("badword", 20L);
        frequencies.put("profane language", 5L);
        frequencies.put("proper language", 15L);
        
        service.rebuildTrie(frequencies);
        
        List<String> suggestions = service.getSuggestions("pro");
        assertEquals(1, suggestions.size());
        assertEquals("proper language", suggestions.get(0));
        
        List<String> badSuggestions = service.getSuggestions("bad");
        assertEquals(0, badSuggestions.size());
    }

    @Test
    public void testBatchFrequencyAggregationSwap() {
        AutocompleteService service = new AutocompleteService(profanityBlacklist);
        
        Map<String, Long> freq1 = new HashMap<>();
        freq1.put("test", 10L);
        service.rebuildTrie(freq1);
        
        assertEquals(1, service.getSuggestions("te").size());
        assertEquals("test", service.getSuggestions("te").get(0));
        
        Map<String, Long> freq2 = new HashMap<>();
        freq2.put("tester", 20L);
        service.rebuildTrie(freq2); // Atomic swap
        
        List<String> suggestions = service.getSuggestions("te");
        assertEquals(1, suggestions.size());
        assertEquals("tester", suggestions.get(0));
    }

    @Test
    public void testEmptyAndUnknownPrefixHandling() {
        AutocompleteService service = new AutocompleteService(profanityBlacklist);
        Map<String, Long> frequencies = new HashMap<>();
        frequencies.put("hello", 10L);
        service.rebuildTrie(frequencies);
        
        assertTrue(service.getSuggestions("").isEmpty());
        assertTrue(service.getSuggestions(null).isEmpty());
        assertTrue(service.getSuggestions("unknown").isEmpty());
    }
}
