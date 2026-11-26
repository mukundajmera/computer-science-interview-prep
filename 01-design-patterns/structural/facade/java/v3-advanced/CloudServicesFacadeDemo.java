/**
 * Facade Pattern - V3 Advanced: Cloud Services SDK.
 *
 * The facade coordinates storage, compute, queueing, and monitoring behind
 * one deploy/rollback API.
 */

import java.util.ArrayList;
import java.util.List;

class DeploymentSummary {
    private final String serviceName;
    private final String artifactUri;
    private final List<String> instanceIds;
    private final String queueName;
    private final String dashboardUrl;

    public DeploymentSummary(
            String serviceName,
            String artifactUri,
            List<String> instanceIds,
            String queueName,
            String dashboardUrl) {
        this.serviceName = serviceName;
        this.artifactUri = artifactUri;
        this.instanceIds = List.copyOf(instanceIds);
        this.queueName = queueName;
        this.dashboardUrl = dashboardUrl;
    }

    public String getServiceName() { return serviceName; }
    public String getArtifactUri() { return artifactUri; }
    public List<String> getInstanceIds() { return instanceIds; }
    public String getQueueName() { return queueName; }
    public String getDashboardUrl() { return dashboardUrl; }
}

class ObjectStorageService {
    public String uploadArtifact(String serviceName, String artifactPath) {
        if (artifactPath == null || artifactPath.isBlank()) {
            throw new IllegalArgumentException("artifactPath is required");
        }
        int slashIndex = artifactPath.lastIndexOf('/');
        String fileName = slashIndex >= 0 ? artifactPath.substring(slashIndex + 1) : artifactPath;
        return "s3://deployments/" + serviceName + "/" + fileName;
    }
}

class ComputeService {
    private final List<String> runningInstances = new ArrayList<>();

    public List<String> startInstances(String serviceName, int workerCount) {
        if (workerCount <= 0) {
            throw new IllegalArgumentException("workerCount must be positive");
        }
        List<String> instanceIds = new ArrayList<>();
        for (int index = 1; index <= workerCount; index++) {
            instanceIds.add("vm-" + serviceName + "-" + index);
        }
        runningInstances.addAll(instanceIds);
        return instanceIds;
    }

    public List<String> stopInstances(List<String> instanceIds) {
        runningInstances.removeAll(instanceIds);
        return List.copyOf(instanceIds);
    }

    public List<String> getRunningInstances() {
        return List.copyOf(runningInstances);
    }
}

class QueueService {
    public String createQueue(String serviceName) {
        return "queue-" + serviceName;
    }
}

class MonitoringService {
    public String createDashboard(String serviceName, List<String> instanceIds) {
        if (instanceIds.isEmpty()) {
            throw new IllegalArgumentException("instanceIds are required");
        }
        return "/dashboards/" + serviceName;
    }
}

class CloudDeploymentFacade {
    private final ObjectStorageService storage;
    private final ComputeService compute;
    private final QueueService queues;
    private final MonitoringService monitoring;

    public CloudDeploymentFacade(
            ObjectStorageService storage,
            ComputeService compute,
            QueueService queues,
            MonitoringService monitoring) {
        this.storage = storage;
        this.compute = compute;
        this.queues = queues;
        this.monitoring = monitoring;
    }

    public DeploymentSummary deployService(String serviceName, String artifactPath, int workerCount) {
        if (serviceName == null || serviceName.isBlank()) {
            throw new IllegalArgumentException("serviceName is required");
        }

        String artifactUri = storage.uploadArtifact(serviceName, artifactPath);
        List<String> instanceIds = compute.startInstances(serviceName, workerCount);
        String queueName = queues.createQueue(serviceName);
        String dashboardUrl = monitoring.createDashboard(serviceName, instanceIds);
        return new DeploymentSummary(serviceName, artifactUri, instanceIds, queueName, dashboardUrl);
    }

    public List<String> rollback(DeploymentSummary deployment) {
        return compute.stopInstances(deployment.getInstanceIds());
    }
}

public class CloudServicesFacadeDemo {
    public static void main(String[] args) {
        CloudDeploymentFacade facade = new CloudDeploymentFacade(
            new ObjectStorageService(),
            new ComputeService(),
            new QueueService(),
            new MonitoringService()
        );

        DeploymentSummary deployment = facade.deployService("feed-api", "build/feed-api.zip", 3);
        System.out.println("Dashboard: " + deployment.getDashboardUrl());
    }
}
