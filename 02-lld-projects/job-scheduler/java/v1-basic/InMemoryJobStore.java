package v1_basic;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class InMemoryJobStore implements JobStore {
    private final Map<String, Job> jobs = new ConcurrentHashMap<>();

    @Override
    public void saveJob(Job job) {
        jobs.put(job.getId(), job);
    }

    @Override
    public Job getJob(String jobId) {
        return jobs.get(jobId);
    }

    @Override
    public List<Job> getAllJobs() {
        return new ArrayList<>(jobs.values());
    }
    
    @Override
    public void removeJob(String jobId) {
        jobs.remove(jobId);
    }

    public String describe() {
        return "InMemoryJobStore: " + jobs.size() + " jobs";
    }
}
