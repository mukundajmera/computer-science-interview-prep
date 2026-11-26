package v1_basic.models;

import v1_basic.enums.*;
import java.time.LocalDateTime;

/**
 * Answer.java - Stack Overflow answer.
 */
public class Answer {
    private final String id;
    private String content;
    private final User author;
    private final Question question;
    private final LocalDateTime createdAt;
    private int votes;
    private boolean isAccepted;

    public Answer(String id, String content, User author, Question question) {
        this.id = id;
        this.content = content;
        this.author = author;
        this.question = question;
        this.createdAt = LocalDateTime.now();
        this.votes = 0;
        this.isAccepted = false;
    }

    public String getId() {
        return id;
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

    public boolean isAccepted() {
        return isAccepted;
    }

    public void vote(int value) {
        this.votes += value;
        author.addReputation(value * 10);
    }

    public void accept() {
        this.isAccepted = true;
        author.addReputation(15);
    }

    @Override
    public String toString() {
        return String.format("A[%s]: by %s (votes: %d%s)",
                id, author.getUsername(), votes, isAccepted ? " ✓" : "");
    }
}
