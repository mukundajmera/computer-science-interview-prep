package tests;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import v1_basic.Post;
import v1_basic.PostSearchService;

import java.util.Arrays;
import java.util.List;

public class PostSearchServiceTest {

    private PostSearchService searchService;

    @BeforeEach
    void setUp() {
        searchService = new PostSearchService();
    }

    @Test
    void testIndexAndSearchByKeyword() {
        Post post1 = new Post("1", "author1", "Hello world and universe", Arrays.asList("hello", "space"), 1000);
        Post post2 = new Post("2", "author2", "The universe is massive", Arrays.asList("space"), 2000);
        
        searchService.indexPost(post1);
        searchService.indexPost(post2);

        List<Post> results = searchService.searchByKeyword("universe", 10);
        Assertions.assertEquals(2, results.size());
        // Results sorted by timestamp descending
        Assertions.assertEquals("2", results.get(0).getPostId());
        Assertions.assertEquals("1", results.get(1).getPostId());

        List<Post> helloResults = searchService.searchByKeyword("hello", 10);
        Assertions.assertEquals(1, helloResults.size());
        Assertions.assertEquals("1", helloResults.get(0).getPostId());
    }

    @Test
    void testSearchByTag() {
        Post post1 = new Post("1", "author1", "Hello world", Arrays.asList("hello", "space"), 1000);
        Post post2 = new Post("2", "author2", "The universe", Arrays.asList("space"), 2000);
        Post post3 = new Post("3", "author3", "Just earth", Arrays.asList("earth"), 3000);
        
        searchService.indexPost(post1);
        searchService.indexPost(post2);
        searchService.indexPost(post3);

        List<Post> results = searchService.searchByTag("space", 10);
        Assertions.assertEquals(2, results.size());
        Assertions.assertEquals("2", results.get(0).getPostId());
        Assertions.assertEquals("1", results.get(1).getPostId());

        List<Post> earthResults = searchService.searchByTag("earth", 10);
        Assertions.assertEquals(1, earthResults.size());
        Assertions.assertEquals("3", earthResults.get(0).getPostId());
    }

    @Test
    void testSearchBooleanAnd() {
        Post post1 = new Post("1", "author1", "Blue sky and green grass", Arrays.asList("nature"), 1000);
        Post post2 = new Post("2", "author2", "Blue ocean and blue sky", Arrays.asList("nature"), 2000);
        Post post3 = new Post("3", "author3", "Green trees", Arrays.asList("nature"), 3000);
        
        searchService.indexPost(post1);
        searchService.indexPost(post2);
        searchService.indexPost(post3);

        List<Post> results = searchService.searchBooleanAnd(Arrays.asList("blue", "sky"), 10);
        Assertions.assertEquals(2, results.size());
        Assertions.assertTrue(results.stream().anyMatch(p -> p.getPostId().equals("1")));
        Assertions.assertTrue(results.stream().anyMatch(p -> p.getPostId().equals("2")));
        
        List<Post> results2 = searchService.searchBooleanAnd(Arrays.asList("blue", "grass"), 10);
        Assertions.assertEquals(1, results2.size());
        Assertions.assertEquals("1", results2.get(0).getPostId());
    }

    @Test
    void testDeletePost() {
        Post post1 = new Post("1", "author1", "Hello world", Arrays.asList("hello", "space"), 1000);
        Post post2 = new Post("2", "author2", "Hello universe", Arrays.asList("space"), 2000);
        
        searchService.indexPost(post1);
        searchService.indexPost(post2);

        List<Post> results = searchService.searchByKeyword("hello", 10);
        Assertions.assertEquals(2, results.size());

        searchService.deletePost("1");

        List<Post> resultsAfterDelete = searchService.searchByKeyword("hello", 10);
        Assertions.assertEquals(1, resultsAfterDelete.size());
        Assertions.assertEquals("2", resultsAfterDelete.get(0).getPostId());
        
        List<Post> tagResultsAfterDelete = searchService.searchByTag("space", 10);
        Assertions.assertEquals(1, tagResultsAfterDelete.size());
        Assertions.assertEquals("2", tagResultsAfterDelete.get(0).getPostId());
    }

    @Test
    void testEmptyResultsAndNullHandling() {
        Post post = new Post("1", "author1", "Hello world", Arrays.asList("hello"), 1000);
        searchService.indexPost(post);

        Assertions.assertTrue(searchService.searchByKeyword("missing", 10).isEmpty());
        Assertions.assertTrue(searchService.searchByTag("missing", 10).isEmpty());
        Assertions.assertTrue(searchService.searchBooleanAnd(Arrays.asList("hello", "missing"), 10).isEmpty());
        Assertions.assertTrue(searchService.searchByKeyword(null, 10).isEmpty());
        Assertions.assertTrue(searchService.searchByKeyword("", 10).isEmpty());
        
        // Ensure indexPost with null doesn't throw
        searchService.indexPost(null);
        searchService.indexPost(new Post(null, "a", "b", null, 0));
        
        // Ensure delete with null or missing doesn't throw
        searchService.deletePost(null);
        searchService.deletePost("missing");
    }
}