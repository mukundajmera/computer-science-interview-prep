"""
Visitor Pattern - Shape Calculator
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
import math

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')



# Visitor Interface
class ShapeVisitor(ABC):
    @abstractmethod
    def visit_circle(self, circle: "Circle") -> None:
        pass
    
    @abstractmethod
    def visit_rectangle(self, rectangle: "Rectangle") -> None:
        pass
    
    @abstractmethod
    def visit_triangle(self, triangle: "Triangle") -> None:
        pass


# Element Interface
class Shape(ABC):
    @abstractmethod
    def accept(self, visitor: ShapeVisitor) -> None:
        pass


# Concrete Elements
@dataclass
class Circle(Shape):
    radius: float
    
    def accept(self, visitor: ShapeVisitor) -> None:
        visitor.visit_circle(self)


@dataclass
class Rectangle(Shape):
    width: float
    height: float
    
    def accept(self, visitor: ShapeVisitor) -> None:
        visitor.visit_rectangle(self)


@dataclass
class Triangle(Shape):
    base: float
    height: float
    
    def accept(self, visitor: ShapeVisitor) -> None:
        visitor.visit_triangle(self)


# Concrete Visitors
class AreaCalculator(ShapeVisitor):
    def __init__(self):
        self.total_area = 0.0
    
    def visit_circle(self, c: Circle) -> None:
        area = math.pi * c.radius ** 2
        print(f"Circle area: {area:.2f}")
        self.total_area += area
    
    def visit_rectangle(self, r: Rectangle) -> None:
        area = r.width * r.height
        print(f"Rectangle area: {area:.2f}")
        self.total_area += area
    
    def visit_triangle(self, t: Triangle) -> None:
        area = 0.5 * t.base * t.height
        print(f"Triangle area: {area:.2f}")
        self.total_area += area


class DrawingVisitor(ShapeVisitor):
    def visit_circle(self, c: Circle) -> None:
        print(f"Drawing ○ Circle with radius {c.radius}")
    
    def visit_rectangle(self, r: Rectangle) -> None:
        print(f"Drawing □ Rectangle {r.width}x{r.height}")
    
    def visit_triangle(self, t: Triangle) -> None:
        print(f"Drawing △ Triangle base={t.base}")


if __name__ == "__main__":
    shapes: List[Shape] = [
        Circle(5),
        Rectangle(4, 6),
        Triangle(3, 4)
    ]
    
    print("=== Area Calculation ===")
    area_calc = AreaCalculator()
    for shape in shapes:
        shape.accept(area_calc)
    print(f"Total area: {area_calc.total_area:.2f}")
    
    print("\n=== Drawing ===")
    drawer = DrawingVisitor()
    for shape in shapes:
        shape.accept(drawer)
