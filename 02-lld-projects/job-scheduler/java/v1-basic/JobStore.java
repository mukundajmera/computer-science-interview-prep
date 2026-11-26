package v1_basic;

import java.util.List;

public interface JobStore {
    void saveJob(Job job);
    Job getJob(String jobId);
    List<Job> getAllJobs();
    void removeJob(String jobId);
}
