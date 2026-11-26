package v1_basic.models;

import v1_basic.enums.*;
import java.time.LocalDateTime;
import java.util.*;

/**
 * Question.java - Stack Overflow question.
 */
public class Question {
    private final String id;
    private String title;
    private String content;
    private final User author;
    private final LocalDateTime createdAt;
    private final List<Answer> answers;
    private final Set<String> tags;
    private int votes;

    public Question(String id, String title, String content, User author) {
        this.id = id;
        this.title = title;
        this.content = content;
        this.author = author;
        this.createdAt = LocalDateTime.now();
        this.answers = new ArrayList<>();
        this.tags = new HashSet<>();
        this.votes = 0;
    }

    public String getId() {
        return id;
    }

    public String getTitle() {
        return title;
    }

    public String getContent() {
        return content;
    }

    public User getAuthor() {
        return author;
    }

    public int getVotes() {
        return votes;
    }

    public void vote(int value) {
        this.votes += value;
        author.addReputation(value * 5);
    }

    public void addAnswer(Answer a) {
        answers.add(a);
    }

    public void addTag(String tag) {
        tags.add(tag);
    }

    public List<Answer> getAnswers() {
        return new ArrayList<>(answers);
    }

    @Override
    public String toString() {
        return String.format("Q[%s]: %s (votes: %d, answers: %d)", id, title, votes, answers.size());
    }
}
