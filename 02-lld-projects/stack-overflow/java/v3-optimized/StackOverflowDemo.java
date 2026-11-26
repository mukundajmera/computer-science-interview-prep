package v3_optimized;

import v3_optimized.models.*;
import v3_optimized.enums.*;
import java.util.*;

/**
 * Stack Overflow - V2 Extended
 * 
 * StackOverflowService with tags and search.
 */
class StackOverflowService {
    private static StackOverflowService instance;
    
    private final Map<String, User> users;
    private final Map<String, Question> questions;
    private final Map<String, Post> posts;
    private final Map<String, Tag> tags;

    private StackOverflowService() {
        this.users = new HashMap<>();
        this.questions = new HashMap<>();
        this.posts = new HashMap<>();
        this.tags = new HashMap<>();
    }

    public static synchronized StackOverflowService getInstance() {
        if (instance == null) instance = new StackOverflowService();
        return instance;
    }

    public static synchronized void resetInstance() { instance = null; }

    public boolean registerUser(User user) {
        if (user == null || users.containsKey(user.getUserId())) return false;
        users.put(user.getUserId(), user);
        return true;
    }

    public User getUser(String userId) { return users.get(userId); }

    public Question postQuestion(String userId, String title, String content, List<String> tagNames) {
        User user = users.get(userId);
        if (user == null) return null;

        Question question = new Question(user, title, content);
        for (String tagName : tagNames) {
            question.addTag(tagName);
            Tag tag = tags.computeIfAbsent(tagName.toLowerCase(), Tag::new);
            tag.addQuestion(question);
        }
        
        user.addQuestion(question);
        questions.put(question.getPostId(), question);
        posts.put(question.getPostId(), question);
        return question;
    }

    public Answer postAnswer(String userId, String questionId, String content) {
        User user = users.get(userId);
        Question question = questions.get(questionId);
        if (user == null || question == null) return null;

        Answer answer = new Answer(user, question, content);
        question.addAnswer(answer);
        user.addAnswer(answer);
        posts.put(answer.getPostId(), answer);
        return answer;
    }

    public boolean vote(String userId, String postId, VoteType voteType) {
        User user = users.get(userId);
        Post post = posts.get(postId);
        if (user == null || post == null) return false;

        Vote vote = new Vote(user, voteType);
        return post.addVote(vote);
    }

    public boolean acceptAnswer(String userId, String answerId) {
        User user = users.get(userId);
        Post post = posts.get(answerId);
        if (user == null || !(post instanceof Answer)) return false;

        Answer answer = (Answer) post;
        Question question = answer.getQuestion();
        if (!question.getAuthor().equals(user)) return false;

        return question.acceptAnswer(answer);
    }

    public Comment addComment(String userId, String postId, String text) {
        User user = users.get(userId);
        Post post = posts.get(postId);
        if (user == null || post == null) return null;

        Comment comment = new Comment(user, text);
        post.addComment(comment);
        return comment;
    }

    public List<Question> searchByTag(String tagName) {
        Tag tag = tags.get(tagName.toLowerCase());
        if (tag == null) return Collections.emptyList();
        return new ArrayList<>(tag.getQuestions());
    }

    public List<Question> searchByKeyword(String keyword) {
        String lower = keyword.toLowerCase();
        List<Question> results = new ArrayList<>();
        for (Question q : questions.values()) {
            if (q.getTitle().toLowerCase().contains(lower) ||
                q.getContent().toLowerCase().contains(lower)) {
                results.add(q);
            }
        }
        return results;
    }

    public List<Question> getTopQuestions(int count) {
        List<Question> sorted = new ArrayList<>(questions.values());
        sorted.sort((a, b) -> b.getScore() - a.getScore());
        return sorted.subList(0, Math.min(count, sorted.size()));
    }

    public List<User> getTopUsers(int count) {
        List<User> sorted = new ArrayList<>(users.values());
        sorted.sort((a, b) -> b.getReputation() - a.getReputation());
        return sorted.subList(0, Math.min(count, sorted.size()));
    }

    public Question getQuestion(String id) { return questions.get(id); }
    public Post getPost(String id) { return posts.get(id); }
    public int getUserCount() { return users.size(); }
    public int getQuestionCount() { return questions.size(); }
}

public class StackOverflowDemo {
    public static void main(String[] args) {
        System.out.println("=== Stack Overflow V2 Demo ===\n");
        
        StackOverflowService so = StackOverflowService.getInstance();
        
        User alice = new User("U001", "Alice", "alice@email.com");
        User bob = new User("U002", "Bob", "bob@email.com");
        User charlie = new User("U003", "Charlie", "charlie@email.com");
        
        so.registerUser(alice);
        so.registerUser(bob);
        so.registerUser(charlie);
        
        Question q1 = so.postQuestion("U001", 
            "How to fix Java NullPointerException?",
            "I keep getting NPE in my code...",
            Arrays.asList("java", "nullpointerexception"));
        
        Question q2 = so.postQuestion("U002",
            "Best Python libraries for ML?",
            "Looking for recommendations...",
            Arrays.asList("python", "machine-learning"));
        
        Answer a1 = so.postAnswer("U002", q1.getPostId(),
            "Check for null before calling methods...");
        Answer a2 = so.postAnswer("U003", q1.getPostId(),
            "Use Optional<T> for null handling...");
        
        // Comments
        so.addComment("U001", a1.getPostId(), "Thanks, that helped!");
        so.addComment("U003", q1.getPostId(), "What version of Java?");
        
        // Voting
        so.vote("U001", a1.getPostId(), VoteType.UPVOTE);
        so.vote("U001", a2.getPostId(), VoteType.UPVOTE);
        so.vote("U003", a1.getPostId(), VoteType.UPVOTE);
        
        // Accept answer
        so.acceptAnswer("U001", a1.getPostId());
        
        System.out.println("--- Sorted Answers ---");
        for (Answer a : q1.getSortedAnswers()) {
            System.out.println(String.format("  [%s] %s (score: %d)", 
                a.isAccepted() ? "✓" : " ",
                a.getAuthor().getName(),
                a.getScore()));
        }
        
        System.out.println("\n--- Comments on Q1 ---");
        for (Comment c : q1.getComments()) {
            System.out.println("  " + c);
        }
        
        System.out.println("\n--- Search 'java' ---");
        for (Question q : so.searchByTag("java")) {
            System.out.println("  " + q.getTitle());
        }
        
        System.out.println("\n--- Top Users ---");
        for (User u : so.getTopUsers(3)) {
            System.out.println("  " + u.getName() + ": " + u.getReputation());
        }
        
        StackOverflowService.resetInstance();
        System.out.println("\n=== Demo Complete ===");
    }
}
