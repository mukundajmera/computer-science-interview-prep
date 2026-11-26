import time
try:
    from .job import Job, RetryPolicy
    from .job_scheduler import JobScheduler
except ImportError:
    from job import Job, RetryPolicy
    from job_scheduler import JobScheduler

def sample_action():
    print("Action executed")

def failing_action():
    print("Failing action executed")
    raise Exception("Simulated failure")

def main():
    scheduler = JobScheduler()
    scheduler.start()

    # Immediate job
    job1 = Job("job1", sample_action)
    scheduler.schedule_job(job1)
    
    # Failing job with retries
    job2 = Job("job2", failing_action, retry_policy=RetryPolicy(max_retries=2, initial_backoff_ms=100))
    scheduler.schedule_job(job2)
    
    # Cron job (executes next minute)
    # job3 = Job("job3", sample_action, cron_expression="* * * * *")
    # scheduler.schedule_job(job3)

    print(scheduler.describe())
    
    time.sleep(2)
    scheduler.stop()
    print("Final status:")
    print(scheduler.get_job("job1").describe())
    print(scheduler.get_job("job2").describe())

if __name__ == "__main__":
    main()
