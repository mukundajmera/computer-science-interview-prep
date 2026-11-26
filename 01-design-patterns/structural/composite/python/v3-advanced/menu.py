"""
Composite Pattern - V3 Advanced: Menu Hierarchy.

Restaurant menus naturally form trees: sections contain items and nested
sections, while clients still need uniform operations such as rendering,
counting, filtering, and price rollups.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


class MenuComponent(ABC):
    """Common interface for menu leaves and menu sections."""

    @abstractmethod
    def item_count(self) -> int:
        """Return the number of menu items in this component."""

    @abstractmethod
    def total_price(self) -> float:
        """Return the sum of item prices in this component."""

    @abstractmethod
    def available_items(self) -> List["MenuItem"]:
        """Return currently available leaf items."""

    @abstractmethod
    def render(self, indent: str = "") -> str:
        """Return a readable menu tree."""


@dataclass
class MenuItem(MenuComponent):
    """Leaf menu item."""

    name: str
    price: float
    vegetarian: bool = False
    available: bool = True

    def item_count(self) -> int:
        return 1

    def total_price(self) -> float:
        return self.price

    def available_items(self) -> List["MenuItem"]:
        return [self] if self.available else []

    def render(self, indent: str = "") -> str:
        marker = "vegetarian" if self.vegetarian else "regular"
        status = "available" if self.available else "sold out"
        return f"{indent}{self.name} - ${self.price:.2f} ({marker}, {status})"


class Menu(MenuComponent):
    """Composite menu section that can contain items or nested sections."""

    def __init__(self, name: str):
        self.name = name
        self._children: List[MenuComponent] = []

    def add(self, component: MenuComponent) -> None:
        self._children.append(component)

    def remove(self, component: MenuComponent) -> None:
        self._children.remove(component)

    def item_count(self) -> int:
        return sum(child.item_count() for child in self._children)

    def total_price(self) -> float:
        return sum(child.total_price() for child in self._children)

    def available_items(self) -> List[MenuItem]:
        items: List[MenuItem] = []
        for child in self._children:
            items.extend(child.available_items())
        return items

    def render(self, indent: str = "") -> str:
        lines = [f"{indent}{self.name} ({self.item_count()} items)"]
        for child in self._children:
            lines.append(child.render(indent + "  "))
        return "\n".join(lines)


if __name__ == "__main__":
    dinner = Menu("Dinner")
    mains = Menu("Mains")
    mains.add(MenuItem("Paneer Bowl", 12.50, vegetarian=True))
    mains.add(MenuItem("Chicken Bowl", 13.75))
    dinner.add(mains)

    print(dinner.render())
    print("Available:", [item.name for item in dinner.available_items()])
