package tests;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import v2_extended.EmailMessage;
import v2_extended.EmailService;
import v2_extended.EmailService.IngestionQueue;
import v2_extended.EmailService.RateLimitExceededException;
import v2_extended.Mailbox;
import v2_extended.ThreadAggregator;

import java.time.Instant;
import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class EmailServiceV2Test {
    private EmailService emailService;

    @BeforeEach
    public void setup() {
        emailService = new EmailService(Arrays.asList("viagra", "lottery", "free money"));
    }

    private EmailMessage msg(String sender, String to, String subject) {
        return new EmailMessage(sender, Arrays.asList(to), null, null, subject, "", null, null, null);
    }

    // --- Parity tests: v2 must keep every v1 guarantee ---

    @Test
    public void testSendAndReceiveEmailDelivery() {
        EmailMessage m = new EmailMessage("alice@demo.com", Arrays.asList("bob@demo.com"), null, null,
                "Hello", "How are you?", null, null, null);
        emailService.sendEmail("alice@demo.com", m);

        Mailbox aliceMailbox = emailService.getMailbox("alice@demo.com");
        assertEquals(1, aliceMailbox.getMessagesInFolder("Sent").size());

        Mailbox bobMailbox = emailService.getMailbox("bob@demo.com");
        assertEquals(1, bobMailbox.getMessagesInFolder("Inbox").size());
        assertEquals("Hello", bobMailbox.getMessagesInFolder("Inbox").get(0).getSubject());
    }

    @Test
    public void testConversationThreadAggregation() {
        EmailMessage msg1 = new EmailMessage("alice@demo.com", Arrays.asList("bob@demo.com"), null, null,
                "Project", "Let's start", null, null, null);
        emailService.sendEmail("alice@demo.com", msg1);

        EmailMessage msg2 = new EmailMessage("bob@demo.com", Arrays.asList("alice@demo.com"), null, null,
                "Re: Project", "Sure", null, msg1.getMessageId(), Arrays.asList(msg1.getMessageId()));
        emailService.sendEmail("bob@demo.com", msg2);

        List<List<EmailMessage>> threads = emailService.getConversationsInFolder("alice@demo.com", "Inbox");
        assertEquals(1, threads.size());
        assertEquals(1, threads.get(0).size());
    }

    @Test
    public void testFolderFilteringAndUnreadCounter() {
        emailService.sendEmail("alice@demo.com", msg("alice@demo.com", "bob@demo.com", "Subject 1"));
        emailService.sendEmail("alice@demo.com", msg("alice@demo.com", "bob@demo.com", "Subject 2"));

        Mailbox bobMailbox = emailService.getMailbox("bob@demo.com");
        assertEquals(2, bobMailbox.getUnreadCount("Inbox"));

        EmailMessage first = bobMailbox.getMessagesInFolder("Inbox").get(0);
        first.markAsRead();
        assertEquals(1, bobMailbox.getUnreadCount("Inbox"));

        EmailMessage second = bobMailbox.getMessagesInFolder("Inbox").get(1);
        bobMailbox.moveMessage(second.getMessageId(), "Trash");
        assertEquals(1, bobMailbox.getMessagesInFolder("Inbox").size());
        assertEquals(1, bobMailbox.getMessagesInFolder("Trash").size());
    }

    @Test
    public void testAttachmentMetadataSeparation() {
        EmailMessage m = new EmailMessage("alice@demo.com", Arrays.asList("bob@demo.com"), null, null,
                "Photos", "See attached", Arrays.asList("s3://bucket/photo1.jpg"), null, null);
        emailService.sendEmail("alice@demo.com", m);

        Mailbox bobMailbox = emailService.getMailbox("bob@demo.com");
        EmailMessage received = bobMailbox.getMessagesInFolder("Inbox").get(0);
        assertEquals(1, received.getAttachmentReferences().size());
        assertEquals("s3://bucket/photo1.jpg", received.getAttachmentReferences().get(0));
    }

    @Test
    public void testSpamKeywordClassification() {
        emailService.sendEmail("alice@demo.com",
            new EmailMessage("alice@demo.com", Arrays.asList("bob@demo.com"), null, null,
                "Hello", "How are you?", null, null, null));
        emailService.sendEmail("eve@demo.com",
            new EmailMessage("eve@demo.com", Arrays.asList("bob@demo.com"), null, null,
                "Win Free Money", "Click here", null, null, null));

        Mailbox bobMailbox = emailService.getMailbox("bob@demo.com");
        assertEquals(1, bobMailbox.getMessagesInFolder("Inbox").size());
        assertEquals(1, bobMailbox.getMessagesInFolder("Spam").size());
        assertEquals("Win Free Money", bobMailbox.getMessagesInFolder("Spam").get(0).getSubject());
    }

    // --- v2 item 1: asynchronous, fail-closed inbound ingestion ---

    @Test
    public void testInboundEnqueueThenProcess() {
        EmailMessage m = msg("ext@yahoo.example", "bob@demo.com", "External");
        assertTrue(emailService.receiveEmailInbound("bob@demo.com", m));
        Mailbox bobMailbox = emailService.getMailbox("bob@demo.com");
        assertEquals(0, bobMailbox.getMessagesInFolder("Inbox").size());
        assertEquals(1, emailService.ingestionQueue.depth());

        assertEquals(1, emailService.processPending());
        assertEquals(1, bobMailbox.getMessagesInFolder("Inbox").size());
        assertEquals(0, emailService.ingestionQueue.depth());
    }

    @Test
    public void testInboundFailsClosedWhenQueueDown() {
        emailService.ingestionQueue.injectFailures(1);
        EmailMessage m = msg("ext@yahoo.example", "bob@demo.com", "Retry me");
        assertFalse(emailService.receiveEmailInbound("bob@demo.com", m));
        assertEquals(0, emailService.ingestionQueue.depth());

        assertTrue(emailService.receiveEmailInbound("bob@demo.com", m));
        assertEquals(1, emailService.processPending());
        assertEquals(1, emailService.getMailbox("bob@demo.com").getMessagesInFolder("Inbox").size());
    }

    @Test
    public void testInboundSpamRoutedAfterProcessing() {
        EmailMessage spam = new EmailMessage("eve@demo.com", Arrays.asList("bob@demo.com"), null, null,
                "Win Free Money", "Click here", null, null, null);
        assertTrue(emailService.receiveEmailInbound("bob@demo.com", spam));
        assertEquals(0, emailService.getMailbox("bob@demo.com").getMessagesInFolder("Spam").size());
        emailService.processPending();
        assertEquals(1, emailService.getMailbox("bob@demo.com").getMessagesInFolder("Spam").size());
    }

    @Test
    public void testInboundFifoOrderPreserved() {
        for (int i = 0; i < 3; i++) {
            emailService.receiveEmailInbound("bob@demo.com", msg("ext@demo.com", "bob@demo.com", "m" + i));
        }
        emailService.processPending();
        List<EmailMessage> inbox = emailService.getMailbox("bob@demo.com").getMessagesInFolder("Inbox");
        assertEquals("m0", inbox.get(0).getSubject());
        assertEquals("m1", inbox.get(1).getSubject());
        assertEquals("m2", inbox.get(2).getSubject());
    }

    // --- v2 item 2: outbound rate limiting ---

    private static class FakeClock {
        long now = 1_000_000L;
        long get() { return now; }
        void advance(long millis) { now += millis; }
    }

    @Test
    public void testRateLimitAllowsWithinWindow() {
        FakeClock clock = new FakeClock();
        EmailService service = new EmailService(null, 3, 60_000L, clock::get, new IngestionQueue());
        for (int i = 0; i < 3; i++) {
            service.sendEmail("alice@demo.com", msg("alice@demo.com", "bob@demo.com", "n" + i));
        }
        assertEquals(3, service.getMailbox("bob@demo.com").getMessagesInFolder("Inbox").size());
    }

    @Test
    public void testRateLimitBlocksOverLimit() {
        FakeClock clock = new FakeClock();
        EmailService service = new EmailService(null, 2, 60_000L, clock::get, new IngestionQueue());
        service.sendEmail("alice@demo.com", msg("alice@demo.com", "bob@demo.com", "n0"));
        service.sendEmail("alice@demo.com", msg("alice@demo.com", "bob@demo.com", "n1"));
        assertThrows(RateLimitExceededException.class,
            () -> service.sendEmail("alice@demo.com", msg("alice@demo.com", "bob@demo.com", "n2")));
        assertEquals(2, service.getMailbox("bob@demo.com").getMessagesInFolder("Inbox").size());
        assertEquals(2, service.getMailbox("alice@demo.com").getMessagesInFolder("Sent").size());
    }

    @Test
    public void testRateLimitWindowResets() {
        FakeClock clock = new FakeClock();
        EmailService service = new EmailService(null, 1, 60_000L, clock::get, new IngestionQueue());
        service.sendEmail("alice@demo.com", msg("alice@demo.com", "bob@demo.com", "first"));
        assertThrows(RateLimitExceededException.class,
            () -> service.sendEmail("alice@demo.com", msg("alice@demo.com", "bob@demo.com", "second")));
        clock.advance(61_000L);
        service.sendEmail("alice@demo.com", msg("alice@demo.com", "bob@demo.com", "after window"));
        List<EmailMessage> inbox = service.getMailbox("bob@demo.com").getMessagesInFolder("Inbox");
        assertEquals(2, inbox.size());
        assertEquals("after window", inbox.get(1).getSubject());
    }

    @Test
    public void testRateLimitIsPerSender() {
        FakeClock clock = new FakeClock();
        EmailService service = new EmailService(null, 1, 60_000L, clock::get, new IngestionQueue());
        service.sendEmail("alice@demo.com", msg("alice@demo.com", "bob@demo.com", "from alice"));
        service.sendEmail("bob@demo.com", msg("bob@demo.com", "alice@demo.com", "from bob"));
        assertEquals(1, service.getMailbox("alice@demo.com").getMessagesInFolder("Inbox").size());
    }

    // --- v2 item 3: order-independent threading ---

    private EmailMessage timedMsg(String subject, long epochSecond, String inReplyTo, List<String> references) {
        EmailMessage m = new EmailMessage("x@demo.com", Arrays.asList("y@demo.com"), null, null,
                subject, "", null, inReplyTo, references);
        m.overrideTimestampForTesting(Instant.ofEpochSecond(epochSecond));
        return m;
    }

    @Test
    public void testThreadingReplyArrivingBeforeParent() {
        EmailMessage parent = timedMsg("Parent", 1L, null, null);
        EmailMessage reply = timedMsg("Re: Parent", 2L, parent.getMessageId(),
                Arrays.asList(parent.getMessageId()));
        // v1 bug scenario: the reply appears BEFORE its parent in the list.
        List<List<EmailMessage>> threads = ThreadAggregator.groupMessagesIntoThreads(
                Arrays.asList(reply, parent));
        assertEquals(1, threads.size());
        assertEquals(2, threads.get(0).size());
        assertEquals("Parent", threads.get(0).get(0).getSubject());
        assertEquals("Re: Parent", threads.get(0).get(1).getSubject());
    }

    @Test
    public void testThreadingMultiLevelChainShuffled() {
        EmailMessage m1 = timedMsg("Root", 1L, null, null);
        EmailMessage m2 = timedMsg("Re: Root", 2L, m1.getMessageId(), Arrays.asList(m1.getMessageId()));
        EmailMessage m3 = timedMsg("Re: Re: Root", 3L, m2.getMessageId(),
                Arrays.asList(m1.getMessageId(), m2.getMessageId()));
        List<List<EmailMessage>> threads = ThreadAggregator.groupMessagesIntoThreads(
                Arrays.asList(m3, m1, m2));
        assertEquals(1, threads.size());
        assertEquals(3, threads.get(0).size());
        assertEquals("Root", threads.get(0).get(0).getSubject());
        assertEquals("Re: Re: Root", threads.get(0).get(2).getSubject());
    }

    @Test
    public void testThreadingDeepChainOutOfOrder() {
        // Java EmailMessage header fields are immutable, so the true
        // header-cycle guard is exercised in the Python suite; here we cover
        // the deepest shuffled chain case.
        EmailMessage a = timedMsg("A", 1L, null, null);
        EmailMessage b = timedMsg("B", 2L, a.getMessageId(), Arrays.asList(a.getMessageId()));
        EmailMessage c = timedMsg("C", 3L, b.getMessageId(), Arrays.asList(b.getMessageId()));
        List<List<EmailMessage>> threads = ThreadAggregator.groupMessagesIntoThreads(
                Arrays.asList(c, b, a));
        assertEquals(1, threads.size());
        assertEquals(3, threads.get(0).size());
    }

    @Test
    public void testThreadingUnknownReferenceStartsNewThread() {
        EmailMessage orphan = timedMsg("Orphan reply", 1L, "missing@elsewhere",
                Arrays.asList("missing@elsewhere"));
        List<List<EmailMessage>> threads = ThreadAggregator.groupMessagesIntoThreads(
                Arrays.asList(orphan));
        assertEquals(1, threads.size());
        assertEquals("Orphan reply", threads.get(0).get(0).getSubject());
    }
}
