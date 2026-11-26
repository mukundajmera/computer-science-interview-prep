package v3;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;

public class DistributedWebCrawlerTest {

    private DistributedWebCrawler crawler;

    @BeforeEach
    public void setup() {
        crawler = new DistributedWebCrawler();
    }

    @Test
    public void testHashRingPartitioning() {
        DistributedWebCrawler.WorkerNode worker1 = crawler.addWorker("worker-1");
        DistributedWebCrawler.WorkerNode worker2 = crawler.addWorker("worker-2");
        DistributedWebCrawler.WorkerNode worker3 = crawler.addWorker("worker-3");

        String url1 = "http://example.com/page1";
        String url2 = "http://test.com/page1";

        crawler.submitToCluster(url1);
        crawler.submitToCluster(url2);

        int totalUrls = worker1.getLocalFrontier().size() + worker2.getLocalFrontier().size() + worker3.getLocalFrontier().size();
        assertEquals(2, totalUrls);

        crawler.submitToCluster("http://example.com/page2");

        DistributedWebCrawler.WorkerNode exampleWorker = null;
        if (worker1.getLocalFrontier().contains(url1)) exampleWorker = worker1;
        else if (worker2.getLocalFrontier().contains(url1)) exampleWorker = worker2;
        else if (worker3.getLocalFrontier().contains(url1)) exampleWorker = worker3;

        assertNotNull(exampleWorker);
        assertTrue(exampleWorker.getLocalFrontier().contains("http://example.com/page2"));
    }

    @Test
    public void testDistributedDeduplication() {
        DistributedWebCrawler.WorkerNode worker = crawler.addWorker("worker-1");

        crawler.submitToCluster("http://example.com/page1");
        crawler.submitToCluster("http://example.com/page1");

        assertEquals(1, worker.getLocalFrontier().size());

        crawler.submitToCluster("http://example.com/page2");
        assertEquals(2, worker.getLocalFrontier().size());
    }

    @Test
    public void testWorkerFailureRecovery() throws InterruptedException {
        DistributedWebCrawler.WorkerNode worker1 = crawler.addWorker("worker-1");

        String url1 = "http://example1.com/page1";
        String url2 = "http://example2.com/page1";

        crawler.submitToCluster(url1);
        crawler.submitToCluster(url2);

        assertEquals(2, worker1.getLocalFrontier().size());

        DistributedWebCrawler.WorkerNode worker2 = crawler.addWorker("worker-2");

        worker1.stop();
        Thread.sleep(100);
        worker2.heartbeat();

        crawler.detectAndRecoverFailures(50);

        assertEquals(2, worker2.getLocalFrontier().size());
        assertTrue(worker2.getLocalFrontier().contains(url1));
        assertTrue(worker2.getLocalFrontier().contains(url2));
    }

    @Test
    public void testPolitenessRateLimiting() {
         DistributedWebCrawler.WorkerNode worker = crawler.addWorker("worker-1");

         for(int i=0; i<10; i++) {
             worker.forceSubmitLocal("http://example.com/page" + i);
         }

         for(int i=0; i<5; i++) {
             assertNotNull(worker.fetchNext());
         }

         assertNull(worker.fetchNext());
    }
}
