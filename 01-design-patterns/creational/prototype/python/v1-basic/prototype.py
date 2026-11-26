"""
Prototype Pattern - V1 Basic

Creates new objects by cloning existing prototypes.
Useful when object creation is expensive or complex.
"""

import copy
from abc import ABC, abstractmethod
from typing import Dict, Any, List, TypeVar, Generic

T = TypeVar('T', bound='Prototype')


# Prototype interface
class Prototype(ABC):
    @abstractmethod
    def clone(self: T) -> T:
        pass


# Concrete Prototype - Shape hierarchy
class Shape(Prototype):
    def __init__(self):
        self.color = "black"
        self.x = 0
        self.y = 0
    
    def set_color(self, color: str) -> 'Shape':
        self.color = color
        return self
    
    def set_position(self, x: int, y: int) -> 'Shape':
        self.x = x
        self.y = y
        return self
    
    @abstractmethod
    def clone(self) -> 'Shape':
        pass
    
    @abstractmethod
    def draw(self) -> None:
        pass
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__} at ({self.x}, {self.y}) [{self.color}]"


class Circle(Shape):
    def __init__(self, radius: int = 10):
        super().__init__()
        self.radius = radius
    
    def set_radius(self, radius: int) -> 'Circle':
        self.radius = radius
        return self
    
    def clone(self) -> 'Circle':
        """Creates a copy of this circle."""
        cloned = Circle(self.radius)
        cloned.color = self.color
        cloned.x = self.x
        cloned.y = self.y
        return cloned
    
    def draw(self) -> None:
        print(f"Drawing {self}")
    
    def __str__(self) -> str:
        return f"Circle(r={self.radius}) at ({self.x}, {self.y}) [{self.color}]"


class Rectangle(Shape):
    def __init__(self, width: int = 20, height: int = 10):
        super().__init__()
        self.width = width
        self.height = height
    
    def set_dimensions(self, width: int, height: int) -> 'Rectangle':
        self.width = width
        self.height = height
        return self
    
    def clone(self) -> 'Rectangle':
        """Creates a copy of this rectangle."""
        cloned = Rectangle(self.width, self.height)
        cloned.color = self.color
        cloned.x = self.x
        cloned.y = self.y
        return cloned
    
    def draw(self) -> None:
        print(f"Drawing {self}")
    
    def __str__(self) -> str:
        return f"Rectangle({self.width}x{self.height}) at ({self.x}, {self.y}) [{self.color}]"


# Complex object with nested objects (demonstrating deep copy)
class Document(Prototype):
    def __init__(self):
        self.title = "Untitled"
        self.content = ""
        self.tags: List[str] = []
        self.metadata: Dict[str, str] = {}
    
    def set_title(self, title: str) -> 'Document':
        self.title = title
        return self
    
    def set_content(self, content: str) -> 'Document':
        self.content = content
        return self
    
    def add_tag(self, tag: str) -> 'Document':
        self.tags.append(tag)
        return self
    
    def add_metadata(self, key: str, value: str) -> 'Document':
        self.metadata[key] = value
        return self
    
    def clone(self) -> 'Document':
        """Creates a deep copy of this document."""
        # Using copy.deepcopy for nested objects
        cloned = Document()
        cloned.title = self.title
        cloned.content = self.content
        cloned.tags = list(self.tags)  # Deep copy list
        cloned.metadata = dict(self.metadata)  # Deep copy dict
        return cloned
    
    def __str__(self) -> str:
        return f"Document{{title='{self.title}', tags={self.tags}, metadata={self.metadata}}}"


# Alternative: Using Python's copy module
class GameCharacter(Prototype):
    """Example using Python's copy module for cloning."""
    
    def __init__(self, name: str, level: int = 1):
        self.name = name
        self.level = level
        self.skills: List[str] = []
        self.inventory: Dict[str, int] = {}
    
    def add_skill(self, skill: str) -> 'GameCharacter':
        self.skills.append(skill)
        return self
    
    def add_item(self, item: str, count: int = 1) -> 'GameCharacter':
        self.inventory[item] = self.inventory.get(item, 0) + count
        return self
    
    def clone(self) -> 'GameCharacter':
        """Uses deepcopy for complete cloning."""
        return copy.deepcopy(self)
    
    def __copy__(self):
        """Shallow copy - nested objects are shared."""
        new = GameCharacter(self.name, self.level)
        new.skills = self.skills  # Shared reference!
        new.inventory = self.inventory  # Shared reference!
        return new
    
    def __deepcopy__(self, memo):
        """Deep copy - all nested objects are copied."""
        new = GameCharacter(self.name, self.level)
        new.skills = copy.deepcopy(self.skills, memo)
        new.inventory = copy.deepcopy(self.inventory, memo)
        return new
    
    def __str__(self) -> str:
        return f"Character({self.name}, Lv.{self.level}, skills={self.skills})"


# Prototype Registry
class PrototypeRegistry:
    """Stores and provides prototype clones."""
    
    _prototypes: Dict[str, Prototype] = {}
    
    @classmethod
    def register(cls, key: str, prototype: Prototype) -> None:
        cls._prototypes[key] = prototype
        print(f"Registered prototype: {key}")
    
    @classmethod
    def get_clone(cls, key: str) -> Prototype:
        prototype = cls._prototypes.get(key)
        if prototype is None:
            raise ValueError(f"Prototype not found: {key}")
        return prototype.clone()
    
    @classmethod
    def contains(cls, key: str) -> bool:
        return key in cls._prototypes
    
    @classmethod
    def list_prototypes(cls) -> None:
        print(f"Available prototypes: {list(cls._prototypes.keys())}")


# Demo
if __name__ == "__main__":
    print("=== Prototype Pattern Demo ===\n")
    
    # Register prototype shapes
    print("--- Registering Prototypes ---")
    PrototypeRegistry.register(
        "red-circle", 
        Circle(50).set_color("red")
    )
    PrototypeRegistry.register(
        "blue-rectangle", 
        Rectangle(100, 50).set_color("blue")
    )
    PrototypeRegistry.register(
        "document-template",
        Document()
            .set_title("Template")
            .set_content("This is a template document.")
            .add_tag("template")
            .add_metadata("version", "1.0")
    )
    
    PrototypeRegistry.list_prototypes()
    
    # Clone shapes
    print("\n--- Cloning Shapes ---\n")
    
    circle1 = PrototypeRegistry.get_clone("red-circle")
    circle1.draw()
    
    circle2 = PrototypeRegistry.get_clone("red-circle")
    circle2.set_position(100, 100)
    circle2.draw()
    
    # Verify independence
    print(f"Same instance? {circle1 is circle2}")  # False
    
    rect1 = PrototypeRegistry.get_clone("blue-rectangle")
    rect1.set_position(50, 50)
    rect1.draw()
    
    # Clone and modify document
    print("\n--- Cloning Documents ---\n")
    
    doc1 = PrototypeRegistry.get_clone("document-template")
    doc1.set_title("Report Q1 2024").add_tag("report").add_metadata("author", "Alice")
    
    doc2 = PrototypeRegistry.get_clone("document-template")
    doc2.set_title("Report Q2 2024").add_tag("report").add_metadata("author", "Bob")
    
    print(f"Doc1: {doc1}")
    print(f"Doc2: {doc2}")
    
    # Verify deep copy
    print("\n--- Verify Deep Copy ---")
    original = Document().set_title("Original").add_tag("original-tag")
    cloned = original.clone()
    cloned.set_title("Cloned").add_tag("cloned-tag")
    
    print(f"Original: {original}")
    print(f"Cloned: {cloned}")
    print(f"Tags are independent: {'cloned-tag' not in str(original)}")
    
    # Game character with deepcopy
    print("\n--- Game Character Cloning ---\n")
    
    template_char = GameCharacter("Hero", 10)
    template_char.add_skill("Slash").add_skill("Block")
    template_char.add_item("Sword", 1).add_item("Potion", 5)
    
    warrior = template_char.clone()
    warrior.name = "Warrior"
    warrior.add_skill("Heavy Strike")
    
    mage = template_char.clone()
    mage.name = "Mage"
    mage.add_skill("Fireball")
    
    print(f"Template: {template_char}")
    print(f"Warrior: {warrior}")
    print(f"Mage: {mage}")
