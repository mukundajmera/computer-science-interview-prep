"""
Facade Pattern - V3 Advanced: Cloud Services SDK.

The facade coordinates storage, compute, queueing, and monitoring subsystems
behind one deploy/rollback API.
"""
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class DeploymentSummary:
    service_name: str
    artifact_uri: str
    instance_ids: List[str]
    queue_name: str
    dashboard_url: str


class ObjectStorageService:
    """Subsystem for artifact storage."""

    def upload_artifact(self, service_name: str, artifact_path: str) -> str:
        if not artifact_path:
            raise ValueError("artifact_path is required")
        return f"s3://deployments/{service_name}/{artifact_path.split('/')[-1]}"


class ComputeService:
    """Subsystem for compute provisioning."""

    def __init__(self):
        self.running_instances: List[str] = []

    def start_instances(self, service_name: str, worker_count: int) -> List[str]:
        if worker_count <= 0:
            raise ValueError("worker_count must be positive")
        instance_ids = [f"vm-{service_name}-{index}" for index in range(1, worker_count + 1)]
        self.running_instances.extend(instance_ids)
        return instance_ids

    def stop_instances(self, instance_ids: List[str]) -> List[str]:
        for instance_id in instance_ids:
            if instance_id in self.running_instances:
                self.running_instances.remove(instance_id)
        return list(instance_ids)


class QueueService:
    """Subsystem for asynchronous work queues."""

    def create_queue(self, service_name: str) -> str:
        return f"queue-{service_name}"


class MonitoringService:
    """Subsystem for dashboards and alerts."""

    def create_dashboard(self, service_name: str, instance_ids: List[str]) -> str:
        if not instance_ids:
            raise ValueError("instance_ids are required")
        return f"/dashboards/{service_name}"


class CloudDeploymentFacade:
    """High-level API for deploying and rolling back a service."""

    def __init__(
        self,
        storage: ObjectStorageService,
        compute: ComputeService,
        queues: QueueService,
        monitoring: MonitoringService,
    ):
        self._storage = storage
        self._compute = compute
        self._queues = queues
        self._monitoring = monitoring

    def deploy_service(
        self,
        service_name: str,
        artifact_path: str,
        worker_count: int,
    ) -> DeploymentSummary:
        if not service_name:
            raise ValueError("service_name is required")

        artifact_uri = self._storage.upload_artifact(service_name, artifact_path)
        instance_ids = self._compute.start_instances(service_name, worker_count)
        queue_name = self._queues.create_queue(service_name)
        dashboard_url = self._monitoring.create_dashboard(service_name, instance_ids)

        return DeploymentSummary(
            service_name=service_name,
            artifact_uri=artifact_uri,
            instance_ids=instance_ids,
            queue_name=queue_name,
            dashboard_url=dashboard_url,
        )

    def rollback(self, deployment: DeploymentSummary) -> List[str]:
        return self._compute.stop_instances(deployment.instance_ids)


if __name__ == "__main__":
    facade = CloudDeploymentFacade(
        ObjectStorageService(),
        ComputeService(),
        QueueService(),
        MonitoringService(),
    )
    print(facade.deploy_service("feed-api", "build/feed-api.zip", 3))
