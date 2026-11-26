"""v3-advanced: Copy-on-Write Versioned Configuration Snapshot Manager.

Applies prototype cloning to immutable configuration state snapshots,
supporting atomic revision commits, rollbacks, and history trails.
"""
from typing import Callable, Dict, List, Optional


class ConfigSnapshot:
    """Snapshot representing a discrete immutable configuration generation."""

    def __init__(self, version: int, properties: Dict[str, str], limits: Dict[str, int]) -> None:
        self.version: int = version
        self._properties: Dict[str, str] = dict(properties)
        self._limits: Dict[str, int] = dict(limits)

    def get_property(self, key: str) -> Optional[str]:
        return self._properties.get(key)

    def get_limit(self, key: str) -> Optional[int]:
        return self._limits.get(key)

    def create_draft(self, next_version: int) -> "ConfigSnapshot":
        """Deep clones properties and limits into a new versioned draft."""
        return ConfigSnapshot(next_version, dict(self._properties), dict(self._limits))

    def set_property(self, key: str, value: str) -> None:
        self._properties[key] = value

    def set_limit(self, key: str, limit: int) -> None:
        self._limits[key] = limit


class ConfigurationManager:
    """Manages versioned configuration commits and prototype rollbacks."""

    def __init__(self, initial_props: Dict[str, str], initial_limits: Dict[str, int]) -> None:
        self.current: ConfigSnapshot = ConfigSnapshot(1, initial_props, initial_limits)
        self._history: List[ConfigSnapshot] = []

    def commit_update(self, updater: Callable[[ConfigSnapshot], None]) -> ConfigSnapshot:
        # Save snapshot of previous state to history
        self._history.append(self.current.create_draft(self.current.version))
        draft = self.current.create_draft(self.current.version + 1)
        updater(draft)
        self.current = draft
        return self.current

    def rollback(self) -> bool:
        if not self._history:
            return False
        self.current = self._history.pop()
        return True

    @property
    def history_depth(self) -> int:
        return len(self._history)
