package v2_extended;

/**
 * v2-extended email service.
 *
 * Improvements over v1-basic (named per the repo rule v1-basic -> v2-extended):
 * 1. Asynchronous, fail-closed inbound ingestion (PITFALLS #3 + FOLLOW-UPS
 *    #3): external mail enters through receiveEmailInbound(), which enqueues
 *    onto an IngestionQueue and acknowledges immediately (the "250 OK"); the
 *    async worker processPending() applies spam classification and delivers.
 *    If the queue is unavailable the worker FAILS CLOSED: it returns false
 *    (a transient 4xx) and keeps nothing, so the sending MTA retries instead
 *    of the message being silently lost. A failure injection hook simulates
 *    the queue outage.
 * 2. Outbound rate limiting (FOLLOW-UPS #2, spam and abuse prevention):
 *    configurable per-sender sends-per-window policy with an injectable
 *    clock; exceeding the window throws RateLimitExceededException before
 *    any delivery happens. Disabled by default (v1 parity).
 * 3. Order-independent threading (PITFALLS #5): see ThreadAggregator.
 */

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.LongSupplier;

public class EmailService {

    public static class RateLimitExceededException extends RuntimeException {
        public RateLimitExceededException(String message) { super(message); }
    }

    static class QueueUnavailableException extends RuntimeException {
        QueueUnavailableException(String message) { super(message); }
    }

    /** Simulated durable queue between the inbound SMTP worker and the
     * async processing pipeline, with an outage injection hook (v2 item 1). */
    public static class IngestionQueue {
        static class Entry {
            final String recipientId;
            final EmailMessage message;
            Entry(String recipientId, EmailMessage message) {
                this.recipientId = recipientId;
                this.message = message;
            }
        }

        private final List<Entry> entries = new ArrayList<>();
        private int failNext = 0;

        public synchronized void injectFailures(int count) {
            this.failNext = count;
        }

        public synchronized void enqueue(String recipientId, EmailMessage message) {
            if (failNext > 0) {
                failNext--;
                throw new QueueUnavailableException("simulated queue outage");
            }
            entries.add(new Entry(recipientId, message));
        }

        synchronized List<Entry> drain() {
            List<Entry> out = new ArrayList<>(entries);
            entries.clear();
            return out;
        }

        public synchronized int depth() {
            return entries.size();
        }
    }

    private final Map<String, Mailbox> userMailboxes;
    private final List<String> spamKeywords;
    private final Integer maxSendsPerWindow;
    private final long rateWindowMillis;
    private final LongSupplier clockMillis;
    private final Map<String, List<Long>> sendTimestamps;
    public final IngestionQueue ingestionQueue;

    public EmailService(List<String> spamKeywords) {
        this(spamKeywords, null, 60_000L, System::currentTimeMillis, new IngestionQueue());
    }

    public EmailService(List<String> spamKeywords, Integer maxSendsPerWindow, long rateWindowMillis,
                        LongSupplier clockMillis, IngestionQueue ingestionQueue) {
        if (maxSendsPerWindow != null && maxSendsPerWindow < 1) {
            throw new IllegalArgumentException("maxSendsPerWindow must be positive or null");
        }
        if (rateWindowMillis <= 0) {
            throw new IllegalArgumentException("rateWindowMillis must be positive");
        }
        if (clockMillis == null || ingestionQueue == null) {
            throw new IllegalArgumentException("clockMillis and ingestionQueue must not be null");
        }
        this.userMailboxes = new ConcurrentHashMap<>();
        this.spamKeywords = spamKeywords == null ? new ArrayList<>() : new ArrayList<>(spamKeywords);
        this.maxSendsPerWindow = maxSendsPerWindow;
        this.rateWindowMillis = rateWindowMillis;
        this.clockMillis = clockMillis;
        this.sendTimestamps = new HashMap<>();
        this.ingestionQueue = ingestionQueue;
    }

    public Mailbox getMailbox(String userId) {
        return userMailboxes.computeIfAbsent(userId, Mailbox::new);
    }

    // --- outbound path (v2 item 2: per-sender rate limiting) ---

    private synchronized void checkRateLimit(String senderId) {
        if (maxSendsPerWindow == null) {
            return;
        }
        long now = clockMillis.getAsLong();
        long windowStart = now - rateWindowMillis;
        List<Long> timestamps = sendTimestamps.getOrDefault(senderId, new ArrayList<>());
        timestamps.removeIf(t -> t <= windowStart);
        if (timestamps.size() >= maxSendsPerWindow) {
            sendTimestamps.put(senderId, timestamps);
            throw new RateLimitExceededException(
                "sender " + senderId + " exceeded " + maxSendsPerWindow + " sends per " + rateWindowMillis + "ms window");
        }
        timestamps.add(now);
        sendTimestamps.put(senderId, timestamps);
    }

    public void sendEmail(String senderId, EmailMessage message) {
        checkRateLimit(senderId);

        EmailMessage senderCopy = new EmailMessage(message);
        senderCopy.markAsRead();

        Mailbox senderMailbox = getMailbox(senderId);
        senderMailbox.addMessage("Sent", senderCopy);

        Set<String> allRecipients = new HashSet<>();
        allRecipients.addAll(message.getToRecipients());
        allRecipients.addAll(message.getCcRecipients());
        allRecipients.addAll(message.getBccRecipients());

        for (String recipientId : allRecipients) {
            EmailMessage recipientCopy = new EmailMessage(message);
            receiveEmail(recipientId, recipientCopy);
        }
    }

    // --- inbound paths ---

    /** Direct internal delivery (v1 parity, used by sendEmail). */
    public void receiveEmail(String recipientId, EmailMessage message) {
        Mailbox recipientMailbox = getMailbox(recipientId);

        if (isSpam(message)) {
            recipientMailbox.addMessage("Spam", message);
        } else {
            recipientMailbox.addMessage("Inbox", message);
        }
    }

    /** External SMTP ingestion (v2 item 1). Returns true on 250 OK: the
     * message is durably queued and will be processed asynchronously.
     * Returns false on transient failure (4xx): nothing was accepted, and
     * the sending MTA is expected to retry, so failing closed loses
     * nothing. */
    public boolean receiveEmailInbound(String recipientId, EmailMessage message) {
        try {
            ingestionQueue.enqueue(recipientId, message);
            return true;
        } catch (QueueUnavailableException e) {
            return false;
        }
    }

    /** Async worker: drain the ingestion queue and deliver. Returns the
     * number of messages delivered. */
    public int processPending() {
        int delivered = 0;
        for (IngestionQueue.Entry entry : ingestionQueue.drain()) {
            receiveEmail(entry.recipientId, entry.message);
            delivered++;
        }
        return delivered;
    }

    // --- classification, search, threading ---

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
