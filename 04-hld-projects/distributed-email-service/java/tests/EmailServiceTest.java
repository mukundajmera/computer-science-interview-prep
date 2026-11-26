package tests;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import v1_basic.EmailMessage;
import v1_basic.EmailService;
import v1_basic.Mailbox;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class EmailServiceTest {
    private EmailService emailService;

    @BeforeEach
    public void setup() {
        emailService = new EmailService(Arrays.asList("viagra", "lottery", "free money"));
    }

    @Test
    public void testSendAndReceiveEmailDelivery() {
        EmailMessage msg = new EmailMessage("alice@demo.com", Arrays.asList("bob@demo.com"), null, null,
                "Hello", "How are you?", null, null, null);
        
        emailService.sendEmail("alice@demo.com", msg);

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

        Mailbox aliceMailbox = emailService.getMailbox("alice@demo.com");
        List<List<EmailMessage>> threads = emailService.getConversationsInFolder("alice@demo.com", "Inbox");
        
        assertEquals(1, threads.size());
        assertEquals(1, threads.get(0).size()); // only msg2 in inbox
    }

    @Test
    public void testFolderFilteringAndUnreadCounter() {
        EmailMessage msg1 = new EmailMessage("alice@demo.com", Arrays.asList("bob@demo.com"), null, null,
                "Subject 1", "Body", null, null, null);
        EmailMessage msg2 = new EmailMessage("alice@demo.com", Arrays.asList("bob@demo.com"), null, null,
                "Subject 2", "Body", null, null, null);
        
        emailService.sendEmail("alice@demo.com", msg1);
        emailService.sendEmail("alice@demo.com", msg2);

        Mailbox bobMailbox = emailService.getMailbox("bob@demo.com");
        assertEquals(2, bobMailbox.getUnreadCount("Inbox"));

        bobMailbox.getMessageById(msg1.getMessageId()).markAsRead();
        assertEquals(1, bobMailbox.getUnreadCount("Inbox"));

        bobMailbox.moveMessage(msg2.getMessageId(), "Trash");
        assertEquals(1, bobMailbox.getMessagesInFolder("Inbox").size());
        assertEquals(0, bobMailbox.getUnreadCount("Inbox"));
        assertEquals(1, bobMailbox.getMessagesInFolder("Trash").size());
    }

    @Test
    public void testAttachmentMetadataSeparation() {
        EmailMessage msg = new EmailMessage("alice@demo.com", Arrays.asList("bob@demo.com"), null, null,
                "Photos", "See attached", Arrays.asList("s3://bucket/photo1.jpg"), null, null);
        emailService.sendEmail("alice@demo.com", msg);

        Mailbox bobMailbox = emailService.getMailbox("bob@demo.com");
        EmailMessage received = bobMailbox.getMessagesInFolder("Inbox").get(0);
        
        assertEquals(1, received.getAttachmentReferences().size());
        assertEquals("s3://bucket/photo1.jpg", received.getAttachmentReferences().get(0));
    }

    @Test
    public void testSpamKeywordClassification() {
        EmailMessage cleanMsg = new EmailMessage("alice@demo.com", Arrays.asList("bob@demo.com"), null, null,
                "Hello", "How are you?", null, null, null);
        EmailMessage spamMsg = new EmailMessage("eve@demo.com", Arrays.asList("bob@demo.com"), null, null,
                "Win Free Money", "Click here", null, null, null);
        
        emailService.sendEmail("alice@demo.com", cleanMsg);
        emailService.sendEmail("eve@demo.com", spamMsg);

        Mailbox bobMailbox = emailService.getMailbox("bob@demo.com");
        assertEquals(1, bobMailbox.getMessagesInFolder("Inbox").size());
        assertEquals(1, bobMailbox.getMessagesInFolder("Spam").size());
        assertEquals("Win Free Money", bobMailbox.getMessagesInFolder("Spam").get(0).getSubject());
    }
}
