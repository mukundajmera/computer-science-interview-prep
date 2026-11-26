package v2_extended.models;

import v2_extended.enums.*;
import java.util.*;

/**
 * User.java - Stack Overflow user.
 */
public class User {
    private final String id;
    private String username;
    private int reputation;
    private final List<Question> questions;
    private final List<Answer> answers;

    public User(String id, String username) {
        this.id = id;
        this.username = username;
        this.reputation = 0;
        this.questions = new ArrayList<>();
        this.answers = new ArrayList<>();
    }

    public String getId() {
        return id;
    }

    public String getUsername() {
        return username;
    }

    public int getReputation() {
        return reputation;
    }

    public void addReputation(int points) {
        this.reputation += points;
    }

    public void addQuestion(Question q) {
        questions.add(q);
    }

    public void addAnswer(Answer a) {
        answers.add(a);
    }

    @Override
    public String toString() {
        return String.format("User[%s, Rep: %d]", username, reputation);
    }
}
