import re
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple

@dataclass
class ASTNode:
    pass

@dataclass
class TextNode(ASTNode):
    text: str

@dataclass
class VariableNode(ASTNode):
    name: str

@dataclass
class IfNode(ASTNode):
    condition_var: str
    body: List[ASTNode]

@dataclass
class ForNode(ASTNode):
    item_name: str
    list_var: str
    body: List[ASTNode]

class PromptSyntaxError(Exception):
    pass

class ASTCompiler:
    """AST template compiler for prompts."""

    # Matches tags like {#if var}, {/if}, {#for item in list}, {/for}, {var}, and escaped {{text}}
    _TOKEN_RE = re.compile(
        r"(\{\{.*?\}\}|\{#if\s+[A-Za-z_][A-Za-z0-9_]*\}|\{/if\}|\{#for\s+[A-Za-z_][A-Za-z0-9_]*\s+in\s+[A-Za-z_][A-Za-z0-9_]*\}|\{/for\}|\{[A-Za-z_][A-Za-z0-9_]*\})"
    )

    @classmethod
    def parse(cls, template: str) -> List[ASTNode]:
        tokens = cls._TOKEN_RE.split(template)
        # Filter out empty tokens
        tokens = [t for t in tokens if t]

        ast, _ = cls._parse_block(tokens, 0, None)
        return ast

    @classmethod
    def _parse_block(cls, tokens: List[str], index: int, end_tag: str = None) -> Tuple[List[ASTNode], int]:
        body = []
        while index < len(tokens):
            token = tokens[index]

            if token == end_tag:
                return body, index + 1

            if token.startswith("{{") and token.endswith("}}"):
                # Escaped braces
                body.append(TextNode(text=token[1:-1]))
                index += 1
            elif token.startswith("{#if "):
                var_name = token[5:-1].strip()
                if_body, index = cls._parse_block(tokens, index + 1, "{/if}")
                body.append(IfNode(condition_var=var_name, body=if_body))
            elif token == "{/if}":
                raise PromptSyntaxError("Unexpected {/if}")
            elif token.startswith("{#for "):
                parts = token[6:-1].strip().split()
                if len(parts) != 3 or parts[1] != "in":
                    raise PromptSyntaxError(f"Invalid for loop syntax: {token}")
                item_name = parts[0]
                list_var = parts[2]
                for_body, index = cls._parse_block(tokens, index + 1, "{/for}")
                body.append(ForNode(item_name=item_name, list_var=list_var, body=for_body))
            elif token == "{/for}":
                raise PromptSyntaxError("Unexpected {/for}")
            elif token.startswith("{") and token.endswith("}"):
                # Variable
                var_name = token[1:-1]
                body.append(VariableNode(name=var_name))
                index += 1
            else:
                # Text
                if body and isinstance(body[-1], TextNode):
                    body[-1].text += token
                else:
                    body.append(TextNode(text=token))
                index += 1

        if end_tag:
            raise PromptSyntaxError(f"Missing closing tag: {end_tag}")

        return body, index

    @classmethod
    def render(cls, ast: List[ASTNode], context: Dict[str, Any]) -> str:
        parts = []
        for node in ast:
            if isinstance(node, TextNode):
                parts.append(node.text)
            elif isinstance(node, VariableNode):
                val = context.get(node.name, "")
                parts.append(str(val))
            elif isinstance(node, IfNode):
                if context.get(node.condition_var):
                    parts.append(cls.render(node.body, context))
            elif isinstance(node, ForNode):
                lst = context.get(node.list_var, [])
                if not isinstance(lst, list):
                    raise ValueError(f"Expected list for {node.list_var}, got {type(lst)}")
                for item in lst:
                    # Provide local context
                    local_ctx = context.copy()
                    local_ctx[node.item_name] = item
                    parts.append(cls.render(node.body, local_ctx))
        return "".join(parts)
