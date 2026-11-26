"""
Proxy Pattern - V2 Variant: Protection Proxy.

Controls document access by checking user roles before delegating to the
real document.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Set


class Document(ABC):
    """Subject interface shared by real documents and document proxies."""

    @abstractmethod
    def read(self) -> str:
        pass

    @abstractmethod
    def write(self, content: str) -> None:
        pass

    @abstractmethod
    def delete(self) -> str:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass


class RealDocument(Document):
    """Real subject containing document data."""

    def __init__(self, name: str):
        self._name = name
        self._content = f"Document content for: {name}"
        self._deleted = False

    def read(self) -> str:
        return self._content

    def write(self, content: str) -> None:
        self._content = content

    def delete(self) -> str:
        self._deleted = True
        return f"Document deleted: {self._name}"

    def get_name(self) -> str:
        return self._name

    @property
    def deleted(self) -> bool:
        return self._deleted


@dataclass(frozen=True)
class User:
    """User identity with role-based permissions."""

    username: str
    roles: Set[str]

    def has_role(self, role: str) -> bool:
        return role in self.roles


class ProtectedDocumentProxy(Document):
    """Protection proxy that enforces reader, writer, and admin roles."""

    def __init__(self, document: RealDocument, user: User):
        self._document = document
        self._user = user

    def read(self) -> str:
        if self._user.has_role("reader") or self._user.has_role("admin"):
            return self._document.read()
        raise PermissionError("Access denied: No read permission")

    def write(self, content: str) -> None:
        if self._user.has_role("writer") or self._user.has_role("admin"):
            self._document.write(content)
            return
        raise PermissionError("Access denied: No write permission")

    def delete(self) -> str:
        if self._user.has_role("admin"):
            return self._document.delete()
        raise PermissionError("Access denied: Admin role required")

    def get_name(self) -> str:
        return self._document.get_name()


if __name__ == "__main__":
    document = RealDocument("sensitive.txt")
    admin_proxy = ProtectedDocumentProxy(document, User("alice", {"admin"}))
    reader_proxy = ProtectedDocumentProxy(document, User("charlie", {"reader"}))

    print(admin_proxy.read())
    admin_proxy.write("Updated content")
    print(reader_proxy.read())
