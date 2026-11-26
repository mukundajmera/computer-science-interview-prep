"""
Bridge Pattern - V2 Pythonic: Shapes + Renderers

The shape hierarchy and renderer hierarchy vary independently. A shape can
switch rendering implementation at runtime without changing shape code.
"""
from abc import ABC, abstractmethod
from typing import List


class Renderer(ABC):
    """Implementation interface for drawing primitives."""

    @abstractmethod
    def render_circle(self, x: int, y: int, radius: int) -> str:
        pass

    @abstractmethod
    def render_rectangle(self, x: int, y: int, width: int, height: int) -> str:
        pass


class SvgRenderer(Renderer):
    """Concrete renderer for SVG-like output."""

    def render_circle(self, x: int, y: int, radius: int) -> str:
        return f'<circle cx="{x}" cy="{y}" r="{radius}" />'

    def render_rectangle(self, x: int, y: int, width: int, height: int) -> str:
        return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" />'


class RasterRenderer(Renderer):
    """Concrete renderer for raster-style drawing commands."""

    def render_circle(self, x: int, y: int, radius: int) -> str:
        return f"Raster circle at ({x}, {y}) with radius {radius}"

    def render_rectangle(self, x: int, y: int, width: int, height: int) -> str:
        return f"Raster rectangle at ({x}, {y}) sized {width}x{height}"


class RecordingRenderer(Renderer):
    """Test-friendly renderer that records primitive calls."""

    def __init__(self) -> None:
        self.commands: List[str] = []

    def render_circle(self, x: int, y: int, radius: int) -> str:
        command = f"circle:{x}:{y}:{radius}"
        self.commands.append(command)
        return command

    def render_rectangle(self, x: int, y: int, width: int, height: int) -> str:
        command = f"rectangle:{x}:{y}:{width}:{height}"
        self.commands.append(command)
        return command


class Shape(ABC):
    """Abstraction that delegates drawing to a renderer implementation."""

    def __init__(self, renderer: Renderer):
        self._renderer = renderer

    def set_renderer(self, renderer: Renderer) -> None:
        self._renderer = renderer

    @abstractmethod
    def draw(self) -> str:
        pass


class Circle(Shape):
    def __init__(self, x: int, y: int, radius: int, renderer: Renderer):
        super().__init__(renderer)
        self.x = x
        self.y = y
        self.radius = radius

    def draw(self) -> str:
        return self._renderer.render_circle(self.x, self.y, self.radius)


class Rectangle(Shape):
    def __init__(self, x: int, y: int, width: int, height: int, renderer: Renderer):
        super().__init__(renderer)
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self) -> str:
        return self._renderer.render_rectangle(self.x, self.y, self.width, self.height)


if __name__ == "__main__":
    shape = Circle(5, 10, 3, SvgRenderer())
    print(shape.draw())
    shape.set_renderer(RasterRenderer())
    print(shape.draw())
