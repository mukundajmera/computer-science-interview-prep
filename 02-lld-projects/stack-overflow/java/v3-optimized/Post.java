package v3_optimized;

import v3_optimized.models.*;
import v3_optimized.enums.*;
import java.time.LocalDateTime;
import java.util.*;

/**
 * Stack Overflow - V2 Extended
 * 
 * Enhanced with comments, reputation thresholds, and search.
 */
class User {
    private final String userId;
    private String name;
    private String email;
    private int reputation;
    private final List<Question> questions;
    private final List<Answer> answers;

    public User(String userId, String name, String email) {
        this.userId = userId;
        this.name = name;
        this.email = email;
        this.reputation = 1;
        this.questions = new ArrayList<>();
        this.answers = new ArrayList<>();
    }

    public synchronized void updateReputation(int delta) {
        this.reputation = Math.max(1, this.reputation + delta);
    }

    public boolean canVote() { return reputation >= 15; }
    public boolean canComment() { return reputation >= 50; }
    public boolean canDownvote() { return reputation >= 125; }

    public void addQuestion(Question q) { questions.add(q); }
    public void addAnswer(Answer a) { answers.add(a); }

    public String getUserId() { return userId; }
    public String getName() { return name; }
    public int getReputation() { return reputation; }
    public List<Question> getQuestions() { return new ArrayList<>(questions); }
    public List<Answer> getAnswers() { return new ArrayList<>(answers); }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof User)) return false;
        return userId.equals(((User) o).userId);
    }

    @Override
    public int hashCode() { return userId.hashCode(); }
}

enum VoteType {
    UPVOTE(1), DOWNVOTE(-1);
    private final int value;
    VoteType(int value) { this.value = value; }
    public int getValue() { return value; }
}

class Vote {
    private final User user;
    private VoteType voteType;
    private final LocalDateTime createdAt;

    public Vote(User user, VoteType voteType) {
        this.user = user;
        this.voteType = voteType;
        this.createdAt = LocalDateTime.now();
    }

    public void changeVote(VoteType newType) { this.voteType = newType; }
    public User getUser() { return user; }
    public VoteType getVoteType() { return voteType; }
}

class Comment {
    private static int commentCounter = 0;
    private final String commentId;
    private final User author;
    private final String text;
    private final LocalDateTime createdAt;

    public Comment(User author, String text) {
        this.commentId = "CMT-" + (++commentCounter);
        this.author = author;
        this.text = text;
        this.createdAt = LocalDateTime.now();
    }

    public String getCommentId() { return commentId; }
    public User getAuthor() { return author; }
    public String getText() { return text; }
    public LocalDateTime getCreatedAt() { return createdAt; }

    @Override
    public String toString() {
        return String.format("%s: %s", author.getName(), text);
    }
}

abstract class Post {
    private static int postCounter = 0;
    
    protected final String postId;
    protected final User author;
    protected String content;
    protected final Map<String, Vote> votes;
    protected final List<Comment> comments;
    protected final LocalDateTime createdAt;
    protected int cachedScore;

    public Post(User author, String content) {
        this.postId = "POST-" + (++postCounter);
        this.author = author;
        this.content = content;
        this.votes = new HashMap<>();
        this.comments = new ArrayList<>();
        this.createdAt = LocalDateTime.now();
        this.cachedScore = 0;
    }

    public boolean addVote(Vote vote) {
        if (vote.getUser().equals(author)) return false;

        Vote existing = votes.get(vote.getUser().getUserId());
        if (existing != null) {
            if (existing.getVoteType() == vote.getVoteType()) return false;
            cachedScore -= existing.getVoteType().getValue();
            author.updateReputation(-getReputationDelta(existing.getVoteType()));
            existing.changeVote(vote.getVoteType());
        } else {
            votes.put(vote.getUser().getUserId(), vote);
        }
        
        cachedScore += vote.getVoteType().getValue();
        author.updateReputation(getReputationDelta(vote.getVoteType()));
        return true;
    }

    public void addComment(Comment comment) {
        comments.add(comment);
    }

    protected int getReputationDelta(VoteType type) {
        return type == VoteType.UPVOTE ? 10 : -2;
    }

    public int getScore() { return cachedScore; }
    public String getPostId() { return postId; }
    public User getAuthor() { return author; }
    public String getContent() { return content; }
    public List<Comment> getComments() { return new ArrayList<>(comments); }
    public LocalDateTime getCreatedAt() { return createdAt; }
}

class Question extends Post {
    private String title;
    private final List<Answer> answers;
    private Answer acceptedAnswer;
    private final Set<String> tags;
    private int viewCount;

    public Question(User author, String title, String content) {
        super(author, content);
        this.title = title;
        this.answers = new ArrayList<>();
        this.acceptedAnswer = null;
        this.tags = new HashSet<>();
        this.viewCount = 0;
    }

    public void addAnswer(Answer answer) { answers.add(answer); }
    
    public boolean acceptAnswer(Answer answer) {
        if (!answers.contains(answer)) return false;
        if (acceptedAnswer != null) acceptedAnswer.setAccepted(false);
        acceptedAnswer = answer;
        answer.setAccepted(true);
        answer.getAuthor().updateReputation(15);
        return true;
    }

    public void addTag(String tag) {
        if (tags.size() < 5) tags.add(tag.toLowerCase());
    }

    public boolean hasTag(String tag) { return tags.contains(tag.toLowerCase()); }
    public void incrementViews() { viewCount++; }

    public String getTitle() { return title; }
    public List<Answer> getAnswers() { return new ArrayList<>(answers); }
    public Answer getAcceptedAnswer() { return acceptedAnswer; }
    public Set<String> getTags() { return new HashSet<>(tags); }
    public int getViewCount() { return viewCount; }
    public int getAnswerCount() { return answers.size(); }

    /**
     * Get answers sorted by score (accepted first).
     */
    public List<Answer> getSortedAnswers() {
        List<Answer> sorted = new ArrayList<>(answers);
        sorted.sort((a, b) -> {
            if (a.isAccepted()) return -1;
            if (b.isAccepted()) return 1;
            return b.getScore() - a.getScore();
        });
        return sorted;
    }
}

class Answer extends Post {
    private final Question question;
    private boolean isAccepted;

    public Answer(User author, Question question, String content) {
        super(author, content);
        this.question = question;
        this.isAccepted = false;
    }

    public void setAccepted(boolean accepted) { this.isAccepted = accepted; }
    public Question getQuestion() { return question; }
    public boolean isAccepted() { return isAccepted; }
}

class Tag {
    private final String name;
    private final Set<Question> questions;

    public Tag(String name) {
        this.name = name.toLowerCase();
        this.questions = new HashSet<>();
    }

    public void addQuestion(Question q) { questions.add(q); }
    public void removeQuestion(Question q) { questions.remove(q); }
    public String getName() { return name; }
    public Set<Question> getQuestions() { return new HashSet<>(questions); }
    public int getQuestionCount() { return questions.size(); }
}
