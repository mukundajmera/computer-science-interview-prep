package v1_basic;

public class JobSchedulerDemo {
    public static void main(String[] args) throws InterruptedException {
        JobScheduler scheduler = new JobScheduler();
        scheduler.start();

        Job job1 = new Job("job1", () -> System.out.println("Action executed"), null, null);
        scheduler.scheduleJob(job1);

        Job job2 = new Job("job2", () -> {
            System.out.println("Failing action executed");
            throw new RuntimeException("Simulated failure");
        }, null, new RetryPolicy(2, 100, 2.0));
        scheduler.scheduleJob(job2);

        System.out.println(scheduler.describe());

        Thread.sleep(2000);
        scheduler.stop();
        System.out.println("Final status:");
        System.out.println(scheduler.getJob("job1").describe());
        System.out.println(scheduler.getJob("job2").describe());
    }
}
