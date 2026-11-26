package v1_basic;

import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.UUID;

public class EmailMessage {
    private final String messageId;
    private final String sender;
    private final List<String> toRecipients;
    private final List<String> ccRecipients;
    private final List<String> bccRecipients;
    private final String subject;
    private final String body;
    private final List<String> attachmentReferences;
    private final String inReplyTo;
    private final List<String> references;
    private final Instant timestamp;
    private boolean isRead;

    public EmailMessage(String sender, List<String> toRecipients, List<String> ccRecipients, List<String> bccRecipients,
                        String subject, String body, List<String> attachmentReferences, String inReplyTo, List<String> references) {
        this.messageId = UUID.randomUUID().toString() + "@distributed-email-service.com";
        this.sender = sender;
        this.toRecipients = toRecipients == null ? Collections.emptyList() : new ArrayList<>(toRecipients);
        this.ccRecipients = ccRecipients == null ? Collections.emptyList() : new ArrayList<>(ccRecipients);
        this.bccRecipients = bccRecipients == null ? Collections.emptyList() : new ArrayList<>(bccRecipients);
        this.subject = subject;
        this.body = body;
        this.attachmentReferences = attachmentReferences == null ? Collections.emptyList() : new ArrayList<>(attachmentReferences);
        this.inReplyTo = inReplyTo;
        this.references = references == null ? Collections.emptyList() : new ArrayList<>(references);
        this.timestamp = Instant.now();
        this.isRead = false;
    }
    
    // Copy constructor to avoid shared read state across mailboxes
    public EmailMessage(EmailMessage other) {
        this.messageId = other.messageId;
        this.sender = other.sender;
        this.toRecipients = other.toRecipients;
        this.ccRecipients = other.ccRecipients;
        this.bccRecipients = other.bccRecipients;
        this.subject = other.subject;
        this.body = other.body;
        this.attachmentReferences = other.attachmentReferences;
        this.inReplyTo = other.inReplyTo;
        this.references = other.references;
        this.timestamp = other.timestamp;
        this.isRead = false; // Fresh copy is unread
    }

    public String getMessageId() { return messageId; }
    public String getSender() { return sender; }
    public List<String> getToRecipients() { return Collections.unmodifiableList(toRecipients); }
    public List<String> getCcRecipients() { return Collections.unmodifiableList(ccRecipients); }
    public List<String> getBccRecipients() { return Collections.unmodifiableList(bccRecipients); }
    public String getSubject() { return subject; }
    public String getBody() { return body; }
    public List<String> getAttachmentReferences() { return Collections.unmodifiableList(attachmentReferences); }
    public String getInReplyTo() { return inReplyTo; }
    public List<String> getReferences() { return Collections.unmodifiableList(references); }
    public Instant getTimestamp() { return timestamp; }
    
    public boolean isRead() { return isRead; }
    public void markAsRead() { this.isRead = true; }
    public void markAsUnread() { this.isRead = false; }
}
