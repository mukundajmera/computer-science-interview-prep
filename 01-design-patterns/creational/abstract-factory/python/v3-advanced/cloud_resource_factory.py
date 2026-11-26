"""v3-advanced: Extensible Cloud Infrastructure Abstract Factory with Dynamic Registry.

Enforces cross-cloud portability across compute, storage, and secrets management
paired with a dynamic provider registry.
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional


class ComputeInstance(ABC):
    @abstractmethod
    def launch(self, instance_type: str) -> str:
        pass

    @abstractmethod
    def get_status(self) -> str:
        pass


class ObjectStorage(ABC):
    @abstractmethod
    def put_object(self, bucket: str, key: str, data: bytes) -> None:
        pass

    @abstractmethod
    def get_object(self, bucket: str, key: str) -> Optional[bytes]:
        pass


class KeyVault(ABC):
    @abstractmethod
    def set_secret(self, key: str, secret: str) -> None:
        pass

    @abstractmethod
    def get_secret(self, key: str) -> Optional[str]:
        pass


class CloudFactory(ABC):
    @abstractmethod
    def get_provider(self) -> str:
        pass

    @abstractmethod
    def create_compute(self) -> ComputeInstance:
        pass

    @abstractmethod
    def create_storage(self) -> ObjectStorage:
        pass

    @abstractmethod
    def create_key_vault(self) -> KeyVault:
        pass


# --- AWS Family ---

class Ec2Compute(ComputeInstance):
    def __init__(self) -> None:
        self._status = "STOPPED"

    def launch(self, instance_type: str) -> str:
        self._status = "RUNNING"
        return f"aws-ec2-{instance_type}-launched"

    def get_status(self) -> str:
        return self._status


class S3Storage(ObjectStorage):
    def __init__(self) -> None:
        self._store: Dict[str, bytes] = {}

    def put_object(self, bucket: str, key: str, data: bytes) -> None:
        self._store[f"{bucket}/{key}"] = data

    def get_object(self, bucket: str, key: str) -> Optional[bytes]:
        return self._store.get(f"{bucket}/{key}")


class AwsSecrets(KeyVault):
    def __init__(self) -> None:
        self._secrets: Dict[str, str] = {}

    def set_secret(self, key: str, secret: str) -> None:
        self._secrets[key] = secret

    def get_secret(self, key: str) -> Optional[str]:
        return self._secrets.get(key)


class AwsCloudFactory(CloudFactory):
    def get_provider(self) -> str:
        return "AWS"

    def create_compute(self) -> ComputeInstance:
        return Ec2Compute()

    def create_storage(self) -> ObjectStorage:
        return S3Storage()

    def create_key_vault(self) -> KeyVault:
        return AwsSecrets()


# --- GCP Family ---

class GceCompute(ComputeInstance):
    def __init__(self) -> None:
        self._status = "TERMINATED"

    def launch(self, instance_type: str) -> str:
        self._status = "ACTIVE"
        return f"gcp-gce-{instance_type}-provisioned"

    def get_status(self) -> str:
        return self._status


class GcsStorage(ObjectStorage):
    def __init__(self) -> None:
        self._store: Dict[str, bytes] = {}

    def put_object(self, bucket: str, key: str, data: bytes) -> None:
        self._store[f"{bucket}/{key}"] = data

    def get_object(self, bucket: str, key: str) -> Optional[bytes]:
        return self._store.get(f"{bucket}/{key}")


class GcpSecrets(KeyVault):
    def __init__(self) -> None:
        self._secrets: Dict[str, str] = {}

    def set_secret(self, key: str, secret: str) -> None:
        self._secrets[key] = secret

    def get_secret(self, key: str) -> Optional[str]:
        return self._secrets.get(key)


class GcpCloudFactory(CloudFactory):
    def get_provider(self) -> str:
        return "GCP"

    def create_compute(self) -> ComputeInstance:
        return GceCompute()

    def create_storage(self) -> ObjectStorage:
        return GcsStorage()

    def create_key_vault(self) -> KeyVault:
        return GcpSecrets()


# --- Registry ---

class CloudProviderRegistry:
    _factories: Dict[str, CloudFactory] = {
        "aws": AwsCloudFactory(),
        "gcp": GcpCloudFactory(),
    }

    @classmethod
    def register(cls, name: str, factory: CloudFactory) -> None:
        cls._factories[name.lower()] = factory

    @classmethod
    def get_factory(cls, name: str) -> CloudFactory:
        factory = cls._factories.get(name.lower())
        if not factory:
            raise ValueError(f"Unknown cloud provider: {name}")
        return factory
