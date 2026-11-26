"""v2-variant: Template Method Pattern for ETL Data Pipelines with Hooks.

Encapsulates the core algorithm skeleton (extract -> transform -> validate hook -> load -> cleanup hook),
allowing subclasses to plug in custom data transforms and validation behaviors.
"""
from abc import ABC, abstractmethod
from typing import List


class EtlPipeline(ABC):
    def __init__(self) -> None:
        self.execution_log: List[str] = []

    def run_pipeline(self, source_uri: str, dest_uri: str) -> bool:
        """The Template Method defining the immutable sequence."""
        self.execution_log.clear()
        self.execution_log.append(f"Started for {source_uri}")

        raw_data = self.extract(source_uri)
        self.execution_log.append(f"Extracted {len(raw_data)} records")

        transformed = self.transform(raw_data)
        self.execution_log.append("Transformed records")

        if self.should_validate() and not self.validate(transformed):
            self.execution_log.append("Validation failed")
            self.on_validation_failure(source_uri)
            return False

        self.load(dest_uri, transformed)
        self.execution_log.append(f"Loaded to {dest_uri}")

        self.post_execution_hook()
        return True

    @abstractmethod
    def extract(self, source: str) -> List[str]:
        pass

    @abstractmethod
    def transform(self, data: List[str]) -> List[str]:
        pass

    @abstractmethod
    def load(self, destination: str, data: List[str]) -> None:
        pass

    # Hooks with defaults
    def should_validate(self) -> bool:
        return True

    def validate(self, data: List[str]) -> bool:
        return bool(data)

    def on_validation_failure(self, source: str) -> None:
        pass

    def post_execution_hook(self) -> None:
        self.execution_log.append("Cleanup hook executed")


class EcommerceSalesEtl(EtlPipeline):
    def extract(self, source: str) -> List[str]:
        return ["order_1:100", "order_2:250", "order_3:40"]

    def transform(self, data: List[str]) -> List[str]:
        return [f"PROCESSED_{item.upper()}" for item in data]

    def load(self, destination: str, data: List[str]) -> None:
        self.execution_log.append(f"Stored to {destination}")


class StrictAuditLogEtl(EtlPipeline):
    def __init__(self, fail_validation: bool = False) -> None:
        super().__init__()
        self._fail_validation = fail_validation

    def extract(self, source: str) -> List[str]:
        return ["log_entry_1", "log_entry_2"]

    def transform(self, data: List[str]) -> List[str]:
        return data

    def validate(self, data: List[str]) -> bool:
        return not self._fail_validation

    def load(self, destination: str, data: List[str]) -> None:
        self.execution_log.append(f"Audited to {destination}")
