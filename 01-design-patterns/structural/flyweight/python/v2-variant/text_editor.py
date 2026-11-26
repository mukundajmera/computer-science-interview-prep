"""
Flyweight Pattern - V2 Variant: Text Editor.

Shares immutable character styles across many glyph occurrences. The glyph
character and coordinates stay extrinsic so a document can render many
characters while storing only a small style pool.
"""
from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class CharacterStyle:
    """Intrinsic text style shared by many glyphs."""

    font_family: str
    font_size: int
    color: str

    def render(self, character: str, x: int, y: int) -> str:
        return (
            f"{character}@({x},{y})"
            f"[{self.font_family}/{self.font_size}/{self.color}]"
        )


class CharacterStyleFactory:
    """Factory that reuses styles with identical intrinsic state."""

    def __init__(self):
        self._styles: Dict[str, CharacterStyle] = {}

    def get_style(self, font_family: str, font_size: int, color: str) -> CharacterStyle:
        key = f"{font_family}:{font_size}:{color}"
        if key not in self._styles:
            self._styles[key] = CharacterStyle(font_family, font_size, color)
        return self._styles[key]

    @property
    def count(self) -> int:
        return len(self._styles)


@dataclass(frozen=True)
class Glyph:
    """Context object holding extrinsic glyph state."""

    character: str
    x: int
    y: int
    style: CharacterStyle

    def render(self) -> str:
        return self.style.render(self.character, self.x, self.y)


class TextDocument:
    """Document that stores glyph positions separately from shared styles."""

    def __init__(self):
        self._style_factory = CharacterStyleFactory()
        self._glyphs: List[Glyph] = []
        self._cursor_x = 0
        self._cursor_y = 0

    def append(self, text: str, font_family: str, font_size: int, color: str) -> None:
        style = self._style_factory.get_style(font_family, font_size, color)
        for character in text:
            self._glyphs.append(Glyph(character, self._cursor_x, self._cursor_y, style))
            self._cursor_x += 1

    def new_line(self) -> None:
        self._cursor_x = 0
        self._cursor_y += 1

    def render_line(self, line_number: int) -> str:
        return " ".join(
            glyph.render() for glyph in self._glyphs if glyph.y == line_number
        )

    @property
    def glyph_count(self) -> int:
        return len(self._glyphs)

    @property
    def style_count(self) -> int:
        return self._style_factory.count


if __name__ == "__main__":
    document = TextDocument()
    document.append("Fly", "Inter", 14, "black")
    document.append("weight", "Inter", 14, "black")
    document.append("!", "Inter", 18, "red")

    print(document.render_line(0))
    print(f"Glyphs: {document.glyph_count}")
    print(f"Shared styles: {document.style_count}")
