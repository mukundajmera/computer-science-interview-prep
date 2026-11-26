"""v2-variant: Game Unit Prototype with Deep Copy and Registry Spawner.

Demonstrates cloning objects with nested mutable collections (abilities list)
to provide fast unit spawning without constructing from scratch.
"""
from abc import ABC, abstractmethod
import copy
from typing import Dict, List, Optional


class GameUnit(ABC):
    @abstractmethod
    def clone_unit(self) -> "GameUnit":
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_health(self) -> int:
        pass

    @abstractmethod
    def take_damage(self, amount: int) -> None:
        pass

    @abstractmethod
    def get_abilities(self) -> List[str]:
        pass

    @abstractmethod
    def add_ability(self, ability: str) -> None:
        pass


class Warrior(GameUnit):
    def __init__(self, name: str, health: int, abilities: List[str]) -> None:
        self._name: str = name
        self._health: int = health
        self._abilities: List[str] = list(abilities)

    def clone_unit(self) -> "Warrior":
        return Warrior(self._name, self._health, list(self._abilities))

    def get_name(self) -> str:
        return self._name

    def get_health(self) -> int:
        return self._health

    def take_damage(self, amount: int) -> None:
        self._health = max(0, self._health - amount)

    def get_abilities(self) -> List[str]:
        return list(self._abilities)

    def add_ability(self, ability: str) -> None:
        self._abilities.append(ability)


class Mage(GameUnit):
    def __init__(self, name: str, health: int, abilities: List[str]) -> None:
        self._name: str = name
        self._health: int = health
        self._abilities: List[str] = list(abilities)

    def clone_unit(self) -> "Mage":
        return Mage(self._name, self._health, list(self._abilities))

    def get_name(self) -> str:
        return self._name

    def get_health(self) -> int:
        return self._health

    def take_damage(self, amount: int) -> None:
        self._health = max(0, self._health - amount)

    def get_abilities(self) -> List[str]:
        return list(self._abilities)

    def add_ability(self, ability: str) -> None:
        self._abilities.append(ability)


class UnitSpawnerRegistry:
    def __init__(self) -> None:
        self._prototypes: Dict[str, GameUnit] = {}

    def register(self, key: str, prototype: GameUnit) -> None:
        self._prototypes[key] = prototype

    def spawn(self, key: str) -> GameUnit:
        proto = self._prototypes.get(key)
        if not proto:
            raise ValueError(f"Unknown prototype: {key}")
        return proto.clone_unit()

    def has_prototype(self, key: str) -> bool:
        return key in self._prototypes
