package v2_extended;

import v2_extended.models.*;
import v2_extended.enums.*;
import v2_extended.enums.VoteType;
import v2_extended.models.*;
import java.util.*;

/**
 * StackOverflowService.java - Singleton Q&A service.
 */
public class StackOverflowService {
    private static StackOverflowService instance;
    private final Map<String, User> users;
    private final Map<String, Question> questions;
    private final Map<String, Answer> answers;
    private int qCounter, aCounter;

    private StackOverflowService() {
        users = new HashMap<>();
        questions = new HashMap<>();
        answers = new HashMap<>();
        qCounter = aCounter = 0;
    }

    public static synchronized StackOverflowService getInstance() {
        if (instance == null)
            instance = new StackOverflowService();
        return instance;
    }

    public void registerUser(User u) {
        users.put(u.getId(), u);
    }

    public Question postQuestion(String userId, String title, String content, String... tags) {
        User user = users.get(userId);
        if (user == null)
            return null;

        String id = "Q-" + (++qCounter);
        Question q = new Question(id, title, content, user);
        for (String tag : tags)
            q.addTag(tag);
        questions.put(id, q);
        user.addQuestion(q);
        return q;
    }

    public Answer postAnswer(String userId, String questionId, String content) {
        User user = users.get(userId);
        Question question = questions.get(questionId);
        if (user == null || question == null)
            return null;

        String id = "A-" + (++aCounter);
        Answer a = new Answer(id, content, user, question);
        answers.put(id, a);
        question.addAnswer(a);
        user.addAnswer(a);
        return a;
    }

    public void vote(String postId, VoteType type) {
        if (postId.startsWith("Q-")) {
            Question q = questions.get(postId);
            if (q != null)
                q.vote(type.getValue());
        } else if (postId.startsWith("A-")) {
            Answer a = answers.get(postId);
            if (a != null)
                a.vote(type.getValue());
        }
    }

    public void acceptAnswer(String answerId) {
        Answer a = answers.get(answerId);
        if (a != null)
            a.accept();
    }

    public List<Question> search(String keyword) {
        List<Question> results = new ArrayList<>();
        for (Question q : questions.values()) {
            if (q.getTitle().toLowerCase().contains(keyword.toLowerCase()) ||
                    q.getContent().toLowerCase().contains(keyword.toLowerCase())) {
                results.add(q);
            }
        }
        return results;
    }
}
