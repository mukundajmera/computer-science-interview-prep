"""
Flyweight Pattern - Python Implementation: Tree Forest
"""
from dataclasses import dataclass
from typing import Dict, List
import random


# Flyweight - Shared intrinsic state
@dataclass(frozen=True)  # Immutable!
class TreeType:
    name: str
    color: str
    texture: str
    
    def __post_init__(self):
        print(f"Creating TreeType: {self.name}")
    
    def draw(self, x: int, y: int) -> None:
        print(f"Drawing {self.name} tree at ({x}, {y})")


# Flyweight Factory
class TreeTypeFactory:
    _tree_types: Dict[str, TreeType] = {}
    
    @classmethod
    def get_tree_type(cls, name: str, color: str, texture: str) -> TreeType:
        key = f"{name}_{color}_{texture}"
        
        if key not in cls._tree_types:
            cls._tree_types[key] = TreeType(name, color, texture)
        
        return cls._tree_types[key]
    
    @classmethod
    def get_type_count(cls) -> int:
        return len(cls._tree_types)

    @classmethod
    def reset(cls) -> None:
        cls._tree_types.clear()


# Context - Contains extrinsic state
class Tree:
    def __init__(self, x: int, y: int, tree_type: TreeType):
        self.x = x  # Extrinsic
        self.y = y  # Extrinsic
        self._type = tree_type  # Reference to flyweight
    
    def draw(self) -> None:
        self._type.draw(self.x, self.y)


# Forest with many trees
class Forest:
    def __init__(self):
        self._trees: List[Tree] = []
    
    def plant_tree(self, x: int, y: int, name: str, color: str, texture: str) -> None:
        tree_type = TreeTypeFactory.get_tree_type(name, color, texture)
        self._trees.append(Tree(x, y, tree_type))
    
    def draw(self) -> None:
        for tree in self._trees:
            tree.draw()
    
    @property
    def tree_count(self) -> int:
        return len(self._trees)


if __name__ == "__main__":
    forest = Forest()
    
    # Plant many trees, but only a few types
    types = ["Oak", "Pine", "Birch"]
    colors = ["Green", "DarkGreen"]
    
    print("=== Creating Forest ===")
    for _ in range(100):
        forest.plant_tree(
            random.randint(0, 1000),
            random.randint(0, 1000),
            random.choice(types),
            random.choice(colors),
            "standard_texture"
        )
    
    print(f"\n=== Statistics ===")
    print(f"Total trees: {forest.tree_count}")
    print(f"Tree types created: {TreeTypeFactory.get_type_count()}")
    print(f"Memory saved: ~{(forest.tree_count - TreeTypeFactory.get_type_count()) * 100} bytes")
