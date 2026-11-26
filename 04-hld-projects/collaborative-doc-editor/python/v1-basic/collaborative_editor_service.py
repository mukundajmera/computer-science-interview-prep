from dataclasses import dataclass
from typing import Optional, Protocol, List, Dict
import threading


@dataclass(frozen=True)
class Document:
    document_id: str
    owner_id: str
    title: str
    version: int


@dataclass(frozen=True)
class DocumentOperation:
    operation_id: str
    base_version: int
    payload: str  # Format: "INSERT index char" or "DELETE index"


@dataclass(frozen=True)
class OperationAck:
    operation_id: str
    applied_version: int
    rebased: bool


class CollaborativeEditorService(Protocol):
    def create_document(self, owner_id: str, title: str) -> Document: ...
    def get_document(self, document_id: str, user_id: str) -> Optional[Document]: ...
    def apply_operation(self, document_id: str, user_id: str, operation: DocumentOperation) -> OperationAck: ...
    def get_document_content(self, document_id: str) -> str: ...


class CollaborativeEditorServiceImpl:
    def __init__(self):
        self._lock = threading.RLock()
        self.documents: Dict[str, Document] = {}
        self.contents: Dict[str, List[str]] = {}
        self.history: Dict[str, List[DocumentOperation]] = {}
        self.doc_counter = 0

    def create_document(self, owner_id: str, title: str) -> Document:
        with self._lock:
            self.doc_counter += 1
            doc_id = f"doc-{self.doc_counter}"
            doc = Document(doc_id, owner_id, title, 0)
            self.documents[doc_id] = doc
            self.contents[doc_id] = []
            self.history[doc_id] = []
            return doc

    def get_document(self, document_id: str, user_id: str) -> Optional[Document]:
        with self._lock:
            return self.documents.get(document_id)
            
    def get_document_content(self, document_id: str) -> str:
        with self._lock:
            if document_id not in self.contents:
                return ""
            return "".join(self.contents[document_id])

    def _transform(self, op1: DocumentOperation, op2: DocumentOperation) -> DocumentOperation:
        # Transform op1 against op2
        # op1 arrives and base_version means it doesn't know about op2
        # So we need to update op1 to account for op2
        # returns op1'
        
        parts1 = op1.payload.split(' ')
        type1 = parts1[0]
        idx1 = int(parts1[1])
        char1 = parts1[2] if len(parts1) > 2 else ""

        if op2.payload == "NOOP":
            return DocumentOperation(op1.operation_id, op2.base_version + 1, op1.payload)
            
        parts2 = op2.payload.split(' ')
        type2 = parts2[0]
        idx2 = int(parts2[1])

        new_idx1 = idx1

        if type1 == "INSERT" and type2 == "INSERT":
            if idx1 > idx2 or (idx1 == idx2 and op1.operation_id > op2.operation_id): # Tie break by op_id
                new_idx1 += 1
        elif type1 == "INSERT" and type2 == "DELETE":
            if idx1 > idx2:
                new_idx1 -= 1
        elif type1 == "DELETE" and type2 == "INSERT":
            if idx1 >= idx2:
                new_idx1 += 1
        elif type1 == "DELETE" and type2 == "DELETE":
            if idx1 > idx2:
                new_idx1 -= 1
            elif idx1 == idx2:
                return None # The character was already deleted

        new_payload = f"{type1} {new_idx1} {char1}".strip()
        return DocumentOperation(op1.operation_id, op2.base_version + 1, new_payload)

    def _apply_transformed_op(self, document_id: str, payload: str):
        parts = payload.split(' ')
        op_type = parts[0]
        idx = int(parts[1])
        
        content = self.contents[document_id]
        
        if op_type == "INSERT":
            char = parts[2]
            content.insert(idx, char)
        elif op_type == "DELETE":
            if 0 <= idx < len(content):
                content.pop(idx)

    def apply_operation(self, document_id: str, user_id: str, operation: DocumentOperation) -> OperationAck:
        with self._lock:
            if document_id not in self.documents:
                raise ValueError("Document not found")
                
            doc = self.documents[document_id]
            doc_history = self.history[document_id]
            
            rebased = False
            current_op = operation
            
            if current_op.base_version < doc.version:
                rebased = True
                # Need to transform against concurrent operations
                concurrent_ops = doc_history[current_op.base_version:]
                for conc_op in concurrent_ops:
                    if current_op is None:
                        break
                    current_op = self._transform(current_op, conc_op)

            if current_op is not None:
                self._apply_transformed_op(document_id, current_op.payload)
                doc_history.append(current_op)
            else:
                # Append a NoOp to maintain history index alignment with document versions
                doc_history.append(DocumentOperation(operation.operation_id, operation.base_version, "NOOP"))
                
            new_version = doc.version + 1
            self.documents[document_id] = Document(doc.document_id, doc.owner_id, doc.title, new_version)
            
            return OperationAck(operation.operation_id, new_version, rebased)

