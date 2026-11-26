package tests;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import v1_basic.CommentIngressService;
import v1_basic.LiveComment;

import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

public class CommentIngressServiceTest {

    @Test
    void testCommentPublishing() {
        CommentIngressService service = new CommentIngressService();
        LiveComment c1 = service.publishComment("v1", "u1", "First!");
        
        Assertions.assertNotNull(c1);
        Assertions.assertEquals("v1", c1.getVideoId());
        Assertions.assertEquals("u1", c1.getUserId());
        Assertions.assertEquals("First!", c1.getMessage());
        Assertions.assertTrue(c1.getSequenceNumber() > 0);
        
        List<LiveComment> recent = service.getRecentComments("v1", 10);
        Assertions.assertEquals(1, recent.size());
        Assertions.assertEquals(c1.getCommentId(), recent.get(0).getCommentId());
    }

    @Test
    void testSequenceMonotonicity() {
        CommentIngressService service = new CommentIngressService();
        LiveComment c1 = service.publishComment("v1", "u1", "msg1");
        LiveComment c2 = service.publishComment("v1", "u2", "msg2");
        LiveComment c3 = service.publishComment("v1", "u3", "msg3");

        Assertions.assertTrue(c1.getSequenceNumber() < c2.getSequenceNumber());
        Assertions.assertTrue(c2.getSequenceNumber() < c3.getSequenceNumber());
        
        List<LiveComment> recent = service.getRecentComments("v1", 2);
        Assertions.assertEquals(2, recent.size());
        // Ordered by recent - check first logic in our test
        // wait, getRecent might order descending based on our implementation logic:
        // long currentSeq = maxSeq - i; 
        // c3 first, then c2
        Assertions.assertEquals(c3.getCommentId(), recent.get(0).getCommentId());
        Assertions.assertEquals(c2.getCommentId(), recent.get(1).getCommentId());
    }

    @Test
    void testRingBufferCapacityRollover() {
        int capacity = 5;
        CommentIngressService service = new CommentIngressService(capacity);
        
        for (int i = 1; i <= 8; i++) {
            service.publishComment("v1", "user", "msg " + i);
        }
        
        List<LiveComment> recent = service.getRecentComments("v1", 10);
        // Even if we asked for 10, capacity is 5, so we should only get 5 comments.
        Assertions.assertEquals(5, recent.size());
        
        // They should be msg 8, 7, 6, 5, 4
        Assertions.assertEquals("msg 8", recent.get(0).getMessage());
        Assertions.assertEquals("msg 7", recent.get(1).getMessage());
        Assertions.assertEquals("msg 6", recent.get(2).getMessage());
        Assertions.assertEquals("msg 5", recent.get(3).getMessage());
        Assertions.assertEquals("msg 4", recent.get(4).getMessage());
    }

    @Test
    void testDeltaPollingViaSequenceNumber() {
        CommentIngressService service = new CommentIngressService();
        service.publishComment("v1", "u1", "msg 1");
        LiveComment c2 = service.publishComment("v1", "u2", "msg 2");
        service.publishComment("v1", "u3", "msg 3");
        service.publishComment("v1", "u4", "msg 4");

        List<LiveComment> delta = service.getCommentsSince("v1", c2.getSequenceNumber());
        Assertions.assertEquals(2, delta.size());
        // getSince returns in ascending order based on our implementation:
        // for (long seq = startSeq; seq <= maxSeq; seq++)
        Assertions.assertEquals("msg 3", delta.get(0).getMessage());
        Assertions.assertEquals("msg 4", delta.get(1).getMessage());
    }

    @Test
    void testMultiThreadedIngress() throws InterruptedException {
        int numThreads = 10;
        int commentsPerThread = 100;
        CommentIngressService service = new CommentIngressService(2000);
        
        ExecutorService executor = Executors.newFixedThreadPool(numThreads);
        CountDownLatch startLatch = new CountDownLatch(1);
        CountDownLatch doneLatch = new CountDownLatch(numThreads);
        
        for (int i = 0; i < numThreads; i++) {
            executor.submit(() -> {
                try {
                    startLatch.await();
                    for (int j = 0; j < commentsPerThread; j++) {
                        service.publishComment("v1", "user", "load test");
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                } finally {
                    doneLatch.countDown();
                }
            });
        }
        
        startLatch.countDown();
        doneLatch.await(5, TimeUnit.SECONDS);
        executor.shutdown();
        
        List<LiveComment> recent = service.getRecentComments("v1", 2000);
        Assertions.assertEquals(numThreads * commentsPerThread, recent.size());
        
        // Ensure no duplicated sequence numbers
        long uniqueSeqs = recent.stream().map(LiveComment::getSequenceNumber).distinct().count();
        Assertions.assertEquals(numThreads * commentsPerThread, uniqueSeqs);
    }
}
