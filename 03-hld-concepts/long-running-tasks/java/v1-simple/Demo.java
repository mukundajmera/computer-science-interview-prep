import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

public class Demo {
    public static void main(String[] args) throws InterruptedException {
        System.out.println("--- Long-Running Tasks Demo ---");

        TaskTracker tracker = new TaskTracker(2);

        // Task 1: Successful task
        System.out.println("\nSubmitting Task 1...");
        CountDownLatch latch1 = new CountDownLatch(1);
        String taskId1 = tracker.submitTask(context -> {
            for (int i = 1; i <= 5; i++) {
                if (context.isCancelled()) return null;
                Thread.sleep(200);
                context.setProgress(i * 20);
                System.out.println("Task 1 Progress: " + context.getTaskInfo().getProgress() + "%");
            }
            return "Task 1 Output";
        }, info -> {
            System.out.println("Callback triggered for Task 1! Status: " + info.getStatus() + ", Result: " + info.getResult());
            latch1.countDown();
        });

        // Polling status
        while (tracker.getTaskInfo(taskId1).getStatus() != TaskTracker.TaskStatus.COMPLETED) {
            Thread.sleep(100);
            System.out.println("Polling Task 1: " + tracker.getTaskInfo(taskId1).getStatus());
        }
        latch1.await(5, TimeUnit.SECONDS);

        // Task 2: Cancelled task
        System.out.println("\nSubmitting Task 2 (Will be cancelled)...");
        CountDownLatch latch2 = new CountDownLatch(1);
        String taskId2 = tracker.submitTask(context -> {
            for (int i = 1; i <= 10; i++) {
                if (context.isCancelled()) {
                    System.out.println("Task 2 detected cancellation internally!");
                    return null;
                }
                Thread.sleep(200);
                context.setProgress(i * 10);
            }
            return "Task 2 Output";
        }, info -> {
            System.out.println("Callback triggered for Task 2! Status: " + info.getStatus());
            latch2.countDown();
        });

        Thread.sleep(300);
        System.out.println("Cancelling Task 2...");
        tracker.cancelTask(taskId2);
        latch2.await(5, TimeUnit.SECONDS);
        System.out.println("Task 2 Final Status: " + tracker.getTaskInfo(taskId2).getStatus());

        // Task 3: Failed task
        System.out.println("\nSubmitting Task 3 (Will fail)...");
        CountDownLatch latch3 = new CountDownLatch(1);
        String taskId3 = tracker.submitTask(context -> {
            Thread.sleep(100);
            throw new RuntimeException("Simulated Failure!");
        }, info -> {
            System.out.println("Callback triggered for Task 3! Status: " + info.getStatus() + ", Error: " + info.getError());
            latch3.countDown();
        });
        latch3.await(5, TimeUnit.SECONDS);

        tracker.shutdown();
        System.out.println("\nDemo completed.");
    }
}