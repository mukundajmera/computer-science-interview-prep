package v1_basic;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

public class EmailService {
    private final Map<String, Mailbox> userMailboxes;
    private final List<String> spamKeywords;

    public EmailService(List<String> spamKeywords) {
        this.userMailboxes = new ConcurrentHashMap<>();
        this.spamKeywords = spamKeywords == null ? new ArrayList<>() : new ArrayList<>(spamKeywords);
    }

    public Mailbox getMailbox(String userId) {
        return userMailboxes.computeIfAbsent(userId, Mailbox::new);
    }

    public void sendEmail(String senderId, EmailMessage message) {
        // Deep copy for the sender to have isolated read state
        EmailMessage senderCopy = new EmailMessage(message);
        senderCopy.markAsRead(); // Typically a sent message is read
        
        Mailbox senderMailbox = getMailbox(senderId);
        senderMailbox.addMessage("Sent", senderCopy);

        Set<String> allRecipients = new HashSet<>();
        allRecipients.addAll(message.getToRecipients());
        allRecipients.addAll(message.getCcRecipients());
        allRecipients.addAll(message.getBccRecipients());

        for (String recipientId : allRecipients) {
            // Deep copy for each recipient
            EmailMessage recipientCopy = new EmailMessage(message);
            receiveEmail(recipientId, recipientCopy);
        }
    }

    public void receiveEmail(String recipientId, EmailMessage message) {
        Mailbox recipientMailbox = getMailbox(recipientId);
        
        if (isSpam(message)) {
            recipientMailbox.addMessage("Spam", message);
        } else {
            recipientMailbox.addMessage("Inbox", message);
        }
    }

    private boolean isSpam(EmailMessage message) {
        String body = message.getBody().toLowerCase();
        String subject = message.getSubject().toLowerCase();
        
        for (String keyword : spamKeywords) {
            if (body.contains(keyword.toLowerCase()) || subject.contains(keyword.toLowerCase())) {
                return true;
            }
        }
        return false;
    }
    
    public List<EmailMessage> searchMessages(String userId, String query) {
        Mailbox mailbox = getMailbox(userId);
        List<EmailMessage> results = new ArrayList<>();
        String lowerQuery = query.toLowerCase();
        
        for (String folder : new String[]{"Inbox", "Sent", "Drafts"}) {
            for (EmailMessage msg : mailbox.getMessagesInFolder(folder)) {
                if (msg.getSubject().toLowerCase().contains(lowerQuery) ||
                    msg.getBody().toLowerCase().contains(lowerQuery) ||
                    msg.getSender().toLowerCase().contains(lowerQuery)) {
                    results.add(msg);
                }
            }
        }
        return results;
    }

    public List<List<EmailMessage>> getConversationsInFolder(String userId, String folderName) {
        Mailbox mailbox = getMailbox(userId);
        List<EmailMessage> folderMessages = mailbox.getMessagesInFolder(folderName);
        return ThreadAggregator.groupMessagesIntoThreads(folderMessages);
    }
}
