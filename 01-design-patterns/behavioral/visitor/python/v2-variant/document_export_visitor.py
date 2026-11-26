"""v2-variant: Document Elements Multi-Format Exporter using Visitor Pattern.

Decouples document representation (Heading, Paragraph, CodeBlock, Hyperlink)
from export targets (Markdown, HTML) using double dispatch.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional


class DocumentVisitor(ABC):
    @abstractmethod
    def visit_heading(self, heading: "Heading") -> None:
        pass

    @abstractmethod
    def visit_paragraph(self, paragraph: "Paragraph") -> None:
        pass

    @abstractmethod
    def visit_code_block(self, code_block: "CodeBlock") -> None:
        pass

    @abstractmethod
    def visit_hyperlink(self, hyperlink: "Hyperlink") -> None:
        pass


class DocumentElement(ABC):
    @abstractmethod
    def accept(self, visitor: DocumentVisitor) -> None:
        pass


class Heading(DocumentElement):
    def __init__(self, text: str, level: int = 1) -> None:
        self.text = text
        self.level = max(1, min(6, level))

    def accept(self, visitor: DocumentVisitor) -> None:
        visitor.visit_heading(self)


class Paragraph(DocumentElement):
    def __init__(self, text: str) -> None:
        self.text = text

    def accept(self, visitor: DocumentVisitor) -> None:
        visitor.visit_paragraph(self)


class CodeBlock(DocumentElement):
    def __init__(self, code: str, language: str = "") -> None:
        self.code = code
        self.language = language

    def accept(self, visitor: DocumentVisitor) -> None:
        visitor.visit_code_block(self)


class Hyperlink(DocumentElement):
    def __init__(self, label: str, url: str) -> None:
        self.label = label
        self.url = url

    def accept(self, visitor: DocumentVisitor) -> None:
        visitor.visit_hyperlink(self)


class MarkdownExportVisitor(DocumentVisitor):
    def __init__(self) -> None:
        self._chunks: List[str] = []

    def visit_heading(self, heading: Heading) -> None:
        prefix = "#" * heading.level
        self._chunks.append(f"{prefix} {heading.text}\n")

    def visit_paragraph(self, paragraph: Paragraph) -> None:
        self._chunks.append(f"{paragraph.text}\n")

    def visit_code_block(self, code_block: CodeBlock) -> None:
        self._chunks.append(f"```{code_block.language}\n{code_block.code}\n```\n")

    def visit_hyperlink(self, hyperlink: Hyperlink) -> None:
        self._chunks.append(f"[{hyperlink.label}]({hyperlink.url})\n")

    def get_exported_output(self) -> str:
        return "\n".join(self._chunks).strip()


class HtmlExportVisitor(DocumentVisitor):
    def __init__(self) -> None:
        self._chunks: List[str] = []

    def visit_heading(self, heading: Heading) -> None:
        self._chunks.append(f"<h{heading.level}>{heading.text}</h{heading.level}>")

    def visit_paragraph(self, paragraph: Paragraph) -> None:
        self._chunks.append(f"<p>{paragraph.text}</p>")

    def visit_code_block(self, code_block: CodeBlock) -> None:
        lang_class = f' class="language-{code_block.language}"' if code_block.language else ""
        self._chunks.append(f"<pre><code{lang_class}>{code_block.code}</code></pre>")

    def visit_hyperlink(self, hyperlink: Hyperlink) -> None:
        self._chunks.append(f'<a href="{hyperlink.url}">{hyperlink.label}</a>')

    def get_exported_output(self) -> str:
        return "\n".join(self._chunks).strip()
