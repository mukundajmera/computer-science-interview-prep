"""v2-variant: UI Dialog Component Mediator Pattern.

Decouples UI form components (TextBox, Checkbox, Button) by concentrating validation
and state synchronization rules inside a central DialogMediator.
"""
from abc import ABC, abstractmethod
from typing import Optional


class DialogMediator(ABC):
    @abstractmethod
    def notify(self, sender: "Component", event: str) -> None:
        pass


class Component:
    def __init__(self) -> None:
        self._mediator: Optional[DialogMediator] = None

    def set_mediator(self, mediator: DialogMediator) -> None:
        self._mediator = mediator


class TextBox(Component):
    def __init__(self) -> None:
        super().__init__()
        self._text: str = ""

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, val: str) -> None:
        self._text = val or ""
        if self._mediator:
            self._mediator.notify(self, "text_changed")

    @property
    def is_empty(self) -> bool:
        return not bool(self._text.strip())


class Checkbox(Component):
    def __init__(self) -> None:
        super().__init__()
        self._checked: bool = False

    @property
    def checked(self) -> bool:
        return self._checked

    @checked.setter
    def checked(self, val: bool) -> None:
        self._checked = bool(val)
        if self._mediator:
            self._mediator.notify(self, "check_changed")


class Button(Component):
    def __init__(self) -> None:
        super().__init__()
        self.enabled: bool = False

    def click(self) -> None:
        if self.enabled and self._mediator:
            self._mediator.notify(self, "click")


class AuthenticationDialogMediator(DialogMediator):
    def __init__(self) -> None:
        self.username_box: TextBox = TextBox()
        self.password_box: TextBox = TextBox()
        self.terms_checkbox: Checkbox = Checkbox()
        self.submit_button: Button = Button()
        self.submitted: bool = False

        self.username_box.set_mediator(self)
        self.password_box.set_mediator(self)
        self.terms_checkbox.set_mediator(self)
        self.submit_button.set_mediator(self)
        self._update_button_state()

    def notify(self, sender: Component, event: str) -> None:
        if event in ("text_changed", "check_changed"):
            self._update_button_state()
        elif event == "click" and sender is self.submit_button:
            if self.submit_button.enabled:
                self.submitted = True

    def _update_button_state(self) -> None:
        valid = (
            not self.username_box.is_empty
            and not self.password_box.is_empty
            and self.terms_checkbox.checked
        )
        self.submit_button.enabled = valid
