import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import v2_extended.PostIngestionServiceV2;

import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class PostSearchServiceV2Test {

    private PostIngestionServiceV2 service;

    @BeforeEach
    void setUp() {
        service = new PostIngestionServiceV2();
        service.upsert("p1", "The quick brown fox jumps over the lazy dog.");
        service.upsert("p2", "A fast brown fox leaps across a sleeping dog.");
        service.upsert("p3", "Dogs are great companions for a walk in the park.");
        service.upsert("p4", "Fox fox fox! Look at that fast brown fox!");
    }

    @Test
    void testBooleanAndSearch() {
        List<String> results = service.search("brown AND fox");
        Assertions.assertEquals(Arrays.asList("p4", "p1", "p2"), results);
        
        List<String> resultsLazy = service.search("lazy AND dog");
        Assertions.assertEquals(Arrays.asList("p1"), resultsLazy);
        
        List<String> resultsNone = service.search("fox AND elephant");
        Assertions.assertTrue(resultsNone.isEmpty());
    }

    @Test
    void testBooleanOrSearch() {
        List<String> results = service.search("lazy OR companions");
        Assertions.assertEquals(Arrays.asList("p3", "p1"), results);
        
        List<String> resultsFox = service.search("fox");
        Assertions.assertEquals(Arrays.asList("p4", "p1", "p2"), resultsFox);
    }

    @Test
    void testRelevanceRanking() {
        List<String> results = service.search("brown OR fox");
        Assertions.assertEquals(Arrays.asList("p4", "p1", "p2"), results);
    }

    @Test
    void testEmptyAndMissingTerms() {
        Assertions.assertTrue(service.search("").isEmpty());
        Assertions.assertTrue(service.search("the and or").isEmpty());
        Assertions.assertTrue(service.search("missingterm").isEmpty());
    }

    @Test
    void testDeterministicTieOrder() {
        service.upsert("t1", "apple");
        service.upsert("t2", "apple");
        service.upsert("t3", "apple");
        
        List<String> results = service.search("apple");
        Assertions.assertEquals(Arrays.asList("t1", "t2", "t3"), results);
    }

    @Test
    void testDeletesAndUpdates() {
        service.upsert("u1", "unique term alpha");
        Assertions.assertEquals(Arrays.asList("u1"), service.search("alpha"));
        
        service.delete("u1");
        Assertions.assertTrue(service.search("alpha").isEmpty());

        service.upsert("u2", "beta gamma");
        Assertions.assertEquals(Arrays.asList("u2"), service.search("beta"));
        
        // update u2 to not have beta
        service.upsert("u2", "delta gamma");
        Assertions.assertTrue(service.search("beta").isEmpty());
        Assertions.assertEquals(Arrays.asList("u2"), service.search("delta"));
    }
}
