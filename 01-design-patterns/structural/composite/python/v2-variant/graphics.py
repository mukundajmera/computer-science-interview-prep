"""
Composite Pattern - V2 Variant: Graphics Groups.

Shapes and groups share the same drawing interface, so a client can move,
measure, and render one shape or an entire nested group uniformly.
"""
from abc import ABC, abstractmethod
from math import pi
from typing import List, Tuple


class Graphic(ABC):
    """Common interface for drawable leaves and composite groups."""

    @abstractmethod
    def move(self, dx: int, dy: int) -> None:
        """Move this graphic by the given delta."""

    @abstractmethod
    def area(self) -> float:
        """Return the total area represented by this graphic."""

    @abstractmethod
    def render(self, indent: str = "") -> str:
        """Return a readable tree representation."""


class Circle(Graphic):
    """Leaf graphic representing a circle."""

    def __init__(self, name: str, x: int, y: int, radius: int):
        self.name = name
        self._x = x
        self._y = y
        self._radius = radius

    @property
    def position(self) -> Tuple[int, int]:
        return self._x, self._y

    def move(self, dx: int, dy: int) -> None:
        self._x += dx
        self._y += dy

    def area(self) -> float:
        return pi * self._radius * self._radius

    def render(self, indent: str = "") -> str:
        return f"{indent}Circle({self.name}) at {self.position}"


class Rectangle(Graphic):
    """Leaf graphic representing a rectangle."""

    def __init__(self, name: str, x: int, y: int, width: int, height: int):
        self.name = name
        self._x = x
        self._y = y
        self._width = width
        self._height = height

    @property
    def position(self) -> Tuple[int, int]:
        return self._x, self._y

    def move(self, dx: int, dy: int) -> None:
        self._x += dx
        self._y += dy

    def area(self) -> float:
        return self._width * self._height

    def render(self, indent: str = "") -> str:
        return f"{indent}Rectangle({self.name}) at {self.position}"


class GraphicGroup(Graphic):
    """Composite graphic that contains leaves or other groups."""

    def __init__(self, name: str):
        self.name = name
        self._children: List[Graphic] = []

    def add(self, graphic: Graphic) -> None:
        self._children.append(graphic)

    def remove(self, graphic: Graphic) -> None:
        self._children.remove(graphic)

    def move(self, dx: int, dy: int) -> None:
        for child in self._children:
            child.move(dx, dy)

    def area(self) -> float:
        return sum(child.area() for child in self._children)

    def render(self, indent: str = "") -> str:
        lines = [f"{indent}Group({self.name}) area={self.area():.2f}"]
        for child in self._children:
            lines.append(child.render(indent + "  "))
        return "\n".join(lines)


if __name__ == "__main__":
    icon = GraphicGroup("profile-icon")
    icon.add(Circle("avatar", 0, 0, 4))
    icon.add(Rectangle("status-badge", 6, 6, 3, 2))

    print(icon.render())
    icon.move(10, 5)
    print("\nAfter move:")
    print(icon.render())
