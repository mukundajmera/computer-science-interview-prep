"""
Flyweight Pattern - V3 Advanced: Icon System.

Shares expensive icon asset data while each toolbar button keeps position,
size, tint, and enabled state as extrinsic context.
"""
from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class IconAsset:
    """Intrinsic icon resource shared across UI placements."""

    name: str
    vector_path: str

    def draw(self, x: int, y: int, size: int, tint: str, enabled: bool) -> str:
        state = "true" if enabled else "false"
        return f"{self.name} at ({x},{y}), size={size}, tint={tint}, enabled={state}"


class IconAssetFactory:
    """Factory that loads each icon asset once."""

    _KNOWN_PATHS = {
        "save": "M4,4 L20,4 L20,20 L4,20 Z",
        "search": "M10,4 A6,6 0 1,0 10,16 L18,24",
        "settings": "M12,2 L15,8 L22,9 L17,14 L18,21 L12,18 L6,21 L7,14 L2,9 L9,8 Z",
    }

    def __init__(self):
        self._assets: Dict[str, IconAsset] = {}

    def get_asset(self, name: str) -> IconAsset:
        if name not in self._assets:
            vector_path = self._KNOWN_PATHS.get(name, f"M0,0 L1,1 /* {name} */")
            self._assets[name] = IconAsset(name, vector_path)
        return self._assets[name]

    @property
    def count(self) -> int:
        return len(self._assets)


@dataclass(frozen=True)
class IconButton:
    """Extrinsic icon placement and interaction state."""

    asset: IconAsset
    x: int
    y: int
    size: int
    tint: str
    enabled: bool

    def render(self) -> str:
        return self.asset.draw(self.x, self.y, self.size, self.tint, self.enabled)


class Toolbar:
    """UI toolbar that reuses icon assets across many buttons."""

    def __init__(self):
        self._asset_factory = IconAssetFactory()
        self._buttons: List[IconButton] = []

    def add_button(
        self, name: str, x: int, y: int, size: int, tint: str, enabled: bool
    ) -> None:
        asset = self._asset_factory.get_asset(name)
        self._buttons.append(IconButton(asset, x, y, size, tint, enabled))

    def render(self) -> List[str]:
        return [button.render() for button in self._buttons]

    @property
    def button_count(self) -> int:
        return len(self._buttons)

    @property
    def asset_count(self) -> int:
        return self._asset_factory.count


if __name__ == "__main__":
    toolbar = Toolbar()
    toolbar.add_button("save", 0, 0, 24, "blue", True)
    toolbar.add_button("save", 32, 0, 32, "gray", False)
    toolbar.add_button("search", 64, 0, 24, "blue", True)

    for command in toolbar.render():
        print(command)
    print(f"Buttons: {toolbar.button_count}")
    print(f"Loaded assets: {toolbar.asset_count}")
