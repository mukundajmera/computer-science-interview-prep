import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;
import java.util.*;
import java.util.concurrent.*;

/**
 * Stack Overflow Test Suite
 */
public class StackOverflowTest {

    private StackOverflowService service;
    private User alice;
    private User bob;
    private User charlie;

    @BeforeEach
    void setUp() {
        StackOverflowService.resetInstance();
        service = StackOverflowService.getInstance();
        
        alice = service.registerUser("U1", "Alice", "alice@test.com");
        bob = service.registerUser("U2", "Bob", "bob@test.com");
        charlie = service.registerUser("U3", "Charlie", "charlie@test.com");
        
        // Give bob and charlie enough reputation to vote
        for (int i = 0; i < 20; i++) {
            bob.updateReputation(10);
            charlie.updateReputation(10);
        }
    }

    @Test
    @DisplayName("User registration works correctly")
    void testUserRegistration() {
        assertNotNull(alice);
        assertEquals("Alice", alice.getName());
        assertEquals(1, alice.getReputation());
    }

    @Test
    @DisplayName("Users can post questions")
    void testPostQuestion() {
        Question question = service.postQuestion(
            alice, 
            "What is Java?", 
            "Please explain Java basics",
            List.of("java", "programming")
        );
        
        assertNotNull(question);
        assertEquals("What is Java?", question.getTitle());
        assertEquals(2, question.getTags().size());
        assertTrue(question.hasTag("java"));
    }

    @Test
    @DisplayName("Users can post answers")
    void testPostAnswer() {
        Question question = service.postQuestion(
            alice, "Test question", "Content",
            List.of("test")
        );
        
        Answer answer = service.postAnswer(bob, question, "This is my answer");
        
        assertNotNull(answer);
        assertEquals(1, question.getAnswerCount());
        assertEquals(bob, answer.getAuthor());
    }

    @Test
    @DisplayName("Voting updates score and reputation")
    void testVoting() {
        Question question = service.postQuestion(
            alice, "Test", "Content", List.of("test")
        );
        
        int initialRep = alice.getReputation();
        
        boolean voted = service.vote(bob, question, VoteType.UPVOTE);
        
        assertTrue(voted);
        assertEquals(1, question.getScore());
        assertEquals(initialRep + 10, alice.getReputation());
    }

    @Test
    @DisplayName("Cannot vote on own post")
    void testCannotVoteOnOwnPost() {
        Question question = service.postQuestion(
            alice, "Test", "Content", List.of("test")
        );
        
        // Give alice voting privileges
        for (int i = 0; i < 20; i++) alice.updateReputation(10);
        
        boolean voted = service.vote(alice, question, VoteType.UPVOTE);
        
        assertFalse(voted);
        assertEquals(0, question.getScore());
    }

    @Test
    @DisplayName("Accepting answer gives reputation")
    void testAcceptAnswer() {
        Question question = service.postQuestion(
            alice, "Test", "Content", List.of("test")
        );
        Answer answer = service.postAnswer(bob, question, "Answer");
        
        int repBefore = bob.getReputation();
        boolean accepted = question.acceptAnswer(answer);
        
        assertTrue(accepted);
        assertTrue(answer.isAccepted());
        assertEquals(repBefore + 15, bob.getReputation());
    }

    @Test
    @DisplayName("Search by tag returns correct questions")
    void testSearchByTag() {
        service.postQuestion(alice, "Java Q", "Content", List.of("java"));
        service.postQuestion(bob, "Python Q", "Content", List.of("python"));
        
        List<Question> results = service.searchByTag("java");
        
        assertEquals(1, results.size());
        assertEquals("Java Q", results.get(0).getTitle());
    }

    @Test
    @DisplayName("Search by keyword returns correct questions")
    void testSearchByKeyword() {
        service.postQuestion(alice, "Java Memory", "About heap", List.of("java"));
        service.postQuestion(bob, "Python Lists", "About lists", List.of("python"));
        
        List<Question> results = service.searchByKeyword("memory");
        
        assertEquals(1, results.size());
        assertTrue(results.get(0).getTitle().contains("Memory"));
    }

    @Test
    @DisplayName("Answer ranking puts accepted first")
    void testAnswerRanking() {
        Question question = service.postQuestion(
            alice, "Test", "Content", List.of("test")
        );
        
        Answer answer1 = service.postAnswer(bob, question, "First answer");
        Answer answer2 = service.postAnswer(charlie, question, "Second answer");
        
        // Upvote first answer multiple times
        User voter = service.registerUser("V1", "Voter", "v@test.com");
        for (int i = 0; i < 20; i++) voter.updateReputation(10);
        service.vote(voter, answer1, VoteType.UPVOTE);
        
        // Accept second answer
        question.acceptAnswer(answer2);
        
        List<Answer> ranked = question.getRankedAnswers();
        
        assertEquals(answer2, ranked.get(0)); // Accepted answer first
        assertEquals(answer1, ranked.get(1));
    }

    @Test
    @DisplayName("Concurrent voting is thread-safe")
    void testConcurrentVoting() throws InterruptedException {
        Question question = service.postQuestion(
            alice, "Test", "Content", List.of("test")
        );
        
        ExecutorService executor = Executors.newFixedThreadPool(10);
        CountDownLatch latch = new CountDownLatch(10);
        
        for (int i = 0; i < 10; i++) {
            final int idx = i;
            executor.submit(() -> {
                try {
                    User voter = service.registerUser("V" + idx, "Voter" + idx, "v" + idx + "@test.com");
                    for (int j = 0; j < 20; j++) voter.updateReputation(10);
                    service.vote(voter, question, VoteType.UPVOTE);
                } finally {
                    latch.countDown();
                }
            });
        }
        
        latch.await(5, TimeUnit.SECONDS);
        executor.shutdown();
        
        assertEquals(10, question.getScore());
    }

    @Test
    @DisplayName("Duplicate detection finds similar questions")
    void testDuplicateDetection() {
        service.postQuestion(alice, "How to sort array in Java", "Content", List.of("java"));
        
        List<Question> duplicates = service.findPotentialDuplicates("sorting array in Java");
        
        assertFalse(duplicates.isEmpty());
    }

    @Test
    @DisplayName("Reputation badges are awarded correctly")
    void testBadges() {
        User user = service.registerUser("TEST", "Test", "test@test.com");
        
        // Initially no badges
        assertTrue(user.getBadges().isEmpty());
        
        // Get to 100 reputation
        for (int i = 0; i < 10; i++) user.updateReputation(10);
        assertTrue(user.getBadges().contains("Bronze"));
        
        // Get to 500 reputation
        for (int i = 0; i < 40; i++) user.updateReputation(10);
        assertTrue(user.getBadges().contains("Silver"));
    }

    @Test
    @DisplayName("Question status can be changed")
    void testQuestionStatus() {
        Question question = service.postQuestion(
            alice, "Test", "Content", List.of("test")
        );
        
        assertEquals(QuestionStatus.OPEN, question.getStatus());
        
        question.closeQuestion();
        assertEquals(QuestionStatus.CLOSED, question.getStatus());
        
        // Cannot add answer to closed question
        assertThrows(IllegalStateException.class, () -> {
            service.postAnswer(bob, question, "Answer");
        });
    }

    @Test
    @DisplayName("Tags track question count correctly")
    void testTagCounts() {
        service.postQuestion(alice, "Q1", "Content", List.of("java"));
        service.postQuestion(bob, "Q2", "Content", List.of("java", "spring"));
        
        Tag javaTag = service.getTag("java");
        
        assertNotNull(javaTag);
        assertEquals(2, javaTag.getQuestionCount());
    }

    @Test
    @DisplayName("Maximum 5 tags per question")
    void testMaxTags() {
        Question question = service.postQuestion(
            alice, "Test", "Content", 
            List.of("tag1", "tag2", "tag3", "tag4", "tag5", "tag6")
        );
        
        assertEquals(5, question.getTags().size());
    }
}
