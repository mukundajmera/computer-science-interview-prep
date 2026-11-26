package tests;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import v3_optimized.PostIngestionServiceV3;

import java.util.Arrays;
import java.util.HashSet;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class PostSearchServiceV3Test {
    private PostIngestionServiceV3 service;

    @BeforeEach
    void setUp() {
        service = new PostIngestionServiceV3();
        service.upsert("p1", "The quick brown fox jumps over the lazy dog.", "idemp1", "us-east");
        service.upsert("p2", "A fast brown fox leaps across a sleeping dog.", "idemp2", "us-east");
        service.upsert("p3", "Dogs are great companions for a walk in the park.", "idemp3", "us-east");
        service.upsert("p4", "Fox fox fox! Look at that fast brown fox!", "idemp4", "us-east");
    }

    @Test
    void testIdempotency() {
        boolean res = service.upsert("p1", "The quick brown fox jumps over the lazy dog.", "idemp1", "us-east");
        assertFalse(res);

        boolean res2 = service.upsert("p5", "Another test.", "idemp5", "us-east");
        assertTrue(res2);
    }

    @Test
    void testBooleanAndSearch() {
        List<String> results = service.search("brown AND fox", "us-east");
        assertEquals(Arrays.asList("p4", "p1", "p2"), results);
    }

    @Test
    void testRelevanceRanking() {
        List<String> results = service.search("brown OR fox", "us-east");
        assertEquals(Arrays.asList("p4", "p1", "p2"), results);
    }

    @Test
    void testEmptyAndMissingTerms() {
        service.upsert("p5", "Just some random text without those keywords.", "idemp5", "us-east");
        
        // Empty tokens
        assertEquals(java.util.Collections.emptyList(), service.search("", "us-east"));
        assertEquals(java.util.Collections.emptyList(), service.search("   ", "us-east"));
        
        // Missing term
        assertEquals(java.util.Collections.emptyList(), service.search("zebra", "us-east"));
        assertEquals(java.util.Collections.emptyList(), service.search("zebra AND fox", "us-east"));
    }

    @Test
    void testDeterministicTieOrder() {
        List<String> results = service.search("brown OR fox", "us-east");
        assertEquals(Arrays.asList("p4", "p1", "p2"), results);
    }

    @Test
    void testDeletesAndUpdates() {
        service.upsert("up1", "apple banana cherry", "idemp_up1", "us-east");
        assertEquals(Arrays.asList("up1"), service.search("banana", "us-east"));
        
        // Update: remove banana
        service.upsert("up1", "apple dog cherry", "idemp_up1_2", "us-east");
        assertEquals(java.util.Collections.emptyList(), service.search("banana", "us-east"));
        assertEquals(Arrays.asList("up1", "p1", "p2"), service.search("dog", "us-east"));
        
        // Delete
        service.delete("up1", "us-east");
        assertEquals(Arrays.asList("p1", "p2"), service.search("dog", "us-east"));
    }
}
