"""
Abstract Factory Pattern - V1 Basic

Creates families of related objects without specifying concrete classes.
Example: Cross-platform UI components.
"""

from abc import ABC, abstractmethod
import platform

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')



# Abstract Products
class Button(ABC):
    @abstractmethod
    def render(self) -> None:
        pass
    
    @abstractmethod
    def on_click(self) -> None:
        pass


class Checkbox(ABC):
    @abstractmethod
    def render(self) -> None:
        pass
    
    @abstractmethod
    def is_checked(self) -> bool:
        pass
    
    @abstractmethod
    def toggle(self) -> None:
        pass


class TextField(ABC):
    @abstractmethod
    def render(self) -> None:
        pass
    
    @abstractmethod
    def get_value(self) -> str:
        pass
    
    @abstractmethod
    def set_value(self, value: str) -> None:
        pass


# Windows Products (Family 1)
class WindowsButton(Button):
    def render(self) -> None:
        print("[Windows Button] Rendering with Win32 API")
    
    def on_click(self) -> None:
        print("[Windows Button] Click handled by Win32")


class WindowsCheckbox(Checkbox):
    def __init__(self):
        self._checked = False
    
    def render(self) -> None:
        state = "[x]" if self._checked else "[ ]"
        print(f"[Windows Checkbox] {state} (Win32 style)")
    
    def is_checked(self) -> bool:
        return self._checked
    
    def toggle(self) -> None:
        self._checked = not self._checked


class WindowsTextField(TextField):
    def __init__(self):
        self._value = ""
    
    def render(self) -> None:
        print("[Windows TextField] +-------------+")
        print(f"                    | {self._value:11} |")
        print("                    +-------------+")
    
    def get_value(self) -> str:
        return self._value
    
    def set_value(self, value: str) -> None:
        self._value = value


# Mac Products (Family 2)
class MacButton(Button):
    def render(self) -> None:
        print("[Mac Button] Rendering with Cocoa framework")
    
    def on_click(self) -> None:
        print("[Mac Button] Click handled by Cocoa")


class MacCheckbox(Checkbox):
    def __init__(self):
        self._checked = False
    
    def render(self) -> None:
        state = "[v]" if self._checked else "[ ]"
        print(f"[Mac Checkbox] {state} (Aqua style)")
    
    def is_checked(self) -> bool:
        return self._checked
    
    def toggle(self) -> None:
        self._checked = not self._checked


class MacTextField(TextField):
    def __init__(self):
        self._value = ""
    
    def render(self) -> None:
        print("[Mac TextField] +-------------+")
        print(f"               | {self._value:11} |")
        print("               +-------------+")
    
    def get_value(self) -> str:
        return self._value
    
    def set_value(self, value: str) -> None:
        self._value = value


# Abstract Factory
class GUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> Button:
        pass
    
    @abstractmethod
    def create_checkbox(self) -> Checkbox:
        pass
    
    @abstractmethod
    def create_text_field(self) -> TextField:
        pass


# Concrete Factories
class WindowsFactory(GUIFactory):
    def create_button(self) -> Button:
        return WindowsButton()
    
    def create_checkbox(self) -> Checkbox:
        return WindowsCheckbox()
    
    def create_text_field(self) -> TextField:
        return WindowsTextField()


class MacFactory(GUIFactory):
    def create_button(self) -> Button:
        return MacButton()
    
    def create_checkbox(self) -> Checkbox:
        return MacCheckbox()
    
    def create_text_field(self) -> TextField:
        return MacTextField()


# Client class - works with any factory
class Application:
    def __init__(self, factory: GUIFactory):
        # Create consistent product family
        self.button = factory.create_button()
        self.checkbox = factory.create_checkbox()
        self.text_field = factory.create_text_field()
    
    def render_ui(self) -> None:
        print("\n--- Rendering Application UI ---")
        self.button.render()
        self.checkbox.render()
        self.text_field.render()
    
    def simulate_interaction(self) -> None:
        print("\n--- Simulating User Interaction ---")
        self.button.on_click()
        self.checkbox.toggle()
        self.checkbox.render()
        self.text_field.set_value("Hello!")
        self.text_field.render()


# Factory provider
class GUIFactoryProvider:
    _factories = {
        "windows": WindowsFactory,
        "win": WindowsFactory,
        "mac": MacFactory,
        "macos": MacFactory,
        "darwin": MacFactory,
    }
    
    @classmethod
    def get_factory(cls, os_name: str) -> GUIFactory:
        factory_class = cls._factories.get(os_name.lower())
        if factory_class is None:
            raise ValueError(f"Unsupported OS: {os_name}")
        return factory_class()
    
    @classmethod
    def get_system_factory(cls) -> GUIFactory:
        system = platform.system().lower()
        if "win" in system:
            return WindowsFactory()
        elif "darwin" in system or "mac" in system:
            return MacFactory()
        else:
            # Default to Windows for demonstration
            return WindowsFactory()


# Demo
if __name__ == "__main__":
    print("=== Abstract Factory Pattern Demo ===")
    
    # Windows application
    print("\n========== WINDOWS APPLICATION ==========")
    windows_factory = GUIFactoryProvider.get_factory("windows")
    windows_app = Application(windows_factory)
    windows_app.render_ui()
    windows_app.simulate_interaction()
    
    # Mac application
    print("\n========== MAC APPLICATION ==========")
    mac_factory = GUIFactoryProvider.get_factory("mac")
    mac_app = Application(mac_factory)
    mac_app.render_ui()
    mac_app.simulate_interaction()
    
    # System-specific (auto-detect)
    print("\n========== SYSTEM APPLICATION ==========")
    system_factory = GUIFactoryProvider.get_system_factory()
    system_app = Application(system_factory)
    system_app.render_ui()
