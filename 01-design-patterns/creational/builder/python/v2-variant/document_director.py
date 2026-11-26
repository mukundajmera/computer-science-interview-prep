"""v2-variant: Builder Pattern with Director and Reusable Concrete Builders.

Decouples document structuring and assembly flows (Director) from formatting
representations (HTML vs. Markdown Concrete Builders).
"""
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional


class DocumentBuilder(ABC):
    """Abstract Builder interface for structured documents."""

    @abstractmethod
    def reset(self) -> "DocumentBuilder":
        pass

    @abstractmethod
    def set_title(self, title: str) -> "DocumentBuilder":
        pass

    @abstractmethod
    def add_section(self, heading: str, body: str) -> "DocumentBuilder":
        pass

    @abstractmethod
    def set_footer(self, footer: str) -> "DocumentBuilder":
        pass

    @abstractmethod
    def get_result(self) -> str:
        pass


class HtmlDocumentBuilder(DocumentBuilder):
    """Concrete Builder generating valid HTML markup representation."""

    def __init__(self) -> None:
        self._title: str = ""
        self._sections: List[Tuple[str, str]] = []
        self._footer: str = ""

    def reset(self) -> "HtmlDocumentBuilder":
        self._title = ""
        self._sections = []
        self._footer = ""
        return self

    def set_title(self, title: str) -> "HtmlDocumentBuilder":
        self._title = title or ""
        return self

    def add_section(self, heading: str, body: str) -> "HtmlDocumentBuilder":
        self._sections.append((heading or "", body or ""))
        return self

    def set_footer(self, footer: str) -> "HtmlDocumentBuilder":
        self._footer = footer or ""
        return self

    def get_result(self) -> str:
        lines = ["<article>"]
        if self._title:
            lines.append(f"  <h1>{self._title}</h1>")
        for heading, body in self._sections:
            lines.append("  <section>")
            lines.append(f"    <h2>{heading}</h2>")
            lines.append(f"    <p>{body}</p>")
            lines.append("  </section>")
        if self._footer:
            lines.append(f"  <footer>{self._footer}</footer>")
        lines.append("</article>")
        return "\n".join(lines)


class MarkdownDocumentBuilder(DocumentBuilder):
    """Concrete Builder generating clean Markdown representation."""

    def __init__(self) -> None:
        self._title: str = ""
        self._sections: List[Tuple[str, str]] = []
        self._footer: str = ""

    def reset(self) -> "MarkdownDocumentBuilder":
        self._title = ""
        self._sections = []
        self._footer = ""
        return self

    def set_title(self, title: str) -> "MarkdownDocumentBuilder":
        self._title = title or ""
        return self

    def add_section(self, heading: str, body: str) -> "MarkdownDocumentBuilder":
        self._sections.append((heading or "", body or ""))
        return self

    def set_footer(self, footer: str) -> "MarkdownDocumentBuilder":
        self._footer = footer or ""
        return self

    def get_result(self) -> str:
        parts: List[str] = []
        if self._title:
            parts.append(f"# {self._title}\n")
        for heading, body in self._sections:
            parts.append(f"## {heading}\n{body}\n")
        if self._footer:
            parts.append(f"---\n*{self._footer}*")
        return "\n".join(parts).strip()


class DocumentDirector:
    """Director that drives the construction sequence across any DocumentBuilder."""

    def __init__(self, builder: DocumentBuilder) -> None:
        if builder is None:
            raise ValueError("Builder cannot be None")
        self._builder: DocumentBuilder = builder

    def change_builder(self, builder: DocumentBuilder) -> None:
        if builder is None:
            raise ValueError("Builder cannot be None")
        self._builder = builder

    def construct_report(self, title: str, findings: List[str], sign_off: str) -> str:
        self._builder.reset()
        self._builder.set_title(title)
        for idx, finding in enumerate(findings, start=1):
            self._builder.add_section(f"Finding {idx}", finding)
        self._builder.set_footer(sign_off)
        return self._builder.get_result()

    def construct_summary(self, title: str, summary_text: str) -> str:
        self._builder.reset()
        self._builder.set_title(title)
        self._builder.add_section("Executive Summary", summary_text)
        self._builder.set_footer("Confidential")
        return self._builder.get_result()
