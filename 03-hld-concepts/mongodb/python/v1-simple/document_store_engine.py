import threading
import uuid
import copy
from typing import Any, Dict, List, Set, Optional

class DocumentStoreEngine:
    class Collection:
        def __init__(self):
            self.documents: Dict[str, Dict[str, Any]] = {}
            self.lock = threading.RLock()
            self.indexes: Dict[str, Dict[Any, Set[str]]] = {}
            self.id_generator = 1

        def _get_field_value(self, doc: Dict[str, Any], field_path: str) -> Any:
            parts = field_path.split('.')
            current = doc
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return None
            return current

        def _set_field_value(self, doc: Dict[str, Any], field_path: str, value: Any):
            parts = field_path.split('.')
            current = doc
            for i in range(len(parts) - 1):
                if parts[i] not in current:
                    current[parts[i]] = {}
                current = current[parts[i]]
            current[parts[-1]] = value

        def _remove_field_value(self, doc: Dict[str, Any], field_path: str):
            parts = field_path.split('.')
            current = doc
            for i in range(len(parts) - 1):
                if isinstance(current, dict) and parts[i] in current:
                    current = current[parts[i]]
                else:
                    return
            if isinstance(current, dict) and parts[-1] in current:
                del current[parts[-1]]

        def insert(self, doc: Dict[str, Any]) -> str:
            with self.lock:
                if "_id" in doc:
                    doc_id = str(doc["_id"])
                else:
                    doc_id = str(self.id_generator)
                    self.id_generator += 1

                doc_copy = copy.deepcopy(doc)
                doc_copy["_id"] = doc_id
                self.documents[doc_id] = doc_copy

                # Update indexes
                for indexed_field, index_map in self.indexes.items():
                    val = self._get_field_value(doc_copy, indexed_field)
                    if val is not None and not isinstance(val, (dict, list)): # Basic index supports hashable types
                        if val not in index_map:
                            index_map[val] = set()
                        index_map[val].add(doc_id)

                return doc_id

        def create_index(self, field: str):
            with self.lock:
                if field not in self.indexes:
                    index_map = {}
                    for doc_id, doc in self.documents.items():
                        val = self._get_field_value(doc, field)
                        if val is not None and not isinstance(val, (dict, list)):
                            if val not in index_map:
                                index_map[val] = set()
                            index_map[val].add(doc_id)
                    self.indexes[field] = index_map

        def _matches(self, doc: Dict[str, Any], query: Dict[str, Any]) -> bool:
            if not query:
                return True

            for field, condition in query.items():
                doc_value = self._get_field_value(doc, field)

                if isinstance(condition, dict):
                    for op, op_val in condition.items():
                        if op == "$eq":
                            if doc_value != op_val:
                                return False
                        elif op == "$gt":
                            if doc_value is None:
                                return False
                            try:
                                if not (doc_value > op_val):
                                    return False
                            except TypeError:
                                return False
                        elif op == "$in":
                            if not isinstance(op_val, (list, tuple, set)):
                                return False
                            if doc_value not in op_val:
                                return False
                        elif op == "$elemMatch":
                            if not isinstance(doc_value, list):
                                return False
                            matched_elem = False
                            for elem in doc_value:
                                if isinstance(elem, dict) and self._matches(elem, op_val):
                                    matched_elem = True
                                    break
                            if not matched_elem:
                                return False
                        else:
                            return False # Unsupported operator
                else:
                    if doc_value != condition:
                        return False
            return True

        def _project(self, doc: Dict[str, Any], projection: Optional[Dict[str, Any]]) -> Dict[str, Any]:
            if not projection:
                return copy.deepcopy(doc)

            include_mode = any(v == 1 for v in projection.values())
            projected = {}

            if include_mode:
                if projection.get("_id", 1) == 1:
                    projected["_id"] = doc.get("_id")

                for key, val in projection.items():
                    if val == 1:
                        doc_val = self._get_field_value(doc, key)
                        if doc_val is not None:
                            self._set_field_value(projected, key, copy.deepcopy(doc_val))
            else:
                projected = copy.deepcopy(doc)
                for key, val in projection.items():
                    if val == 0:
                        self._remove_field_value(projected, key)

            return projected

        def find(self, query: Optional[Dict[str, Any]] = None, projection: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
            with self.lock:
                query = query or {}
                candidate_ids: Optional[Set[str]] = None

                # Index usage
                for field, condition in query.items():
                    if field in self.indexes:
                        if isinstance(condition, dict):
                            if "$eq" in condition:
                                val = condition["$eq"]
                                indexed_ids = self.indexes[field].get(val, set())
                                if candidate_ids is None:
                                    candidate_ids = set(indexed_ids)
                                else:
                                    candidate_ids.intersection_update(indexed_ids)
                        else:
                            if not isinstance(condition, (dict, list)):
                                indexed_ids = self.indexes[field].get(condition, set())
                                if candidate_ids is None:
                                    candidate_ids = set(indexed_ids)
                                else:
                                    candidate_ids.intersection_update(indexed_ids)

                if candidate_ids is not None:
                    docs_to_search = [self.documents[doc_id] for doc_id in candidate_ids if doc_id in self.documents]
                else:
                    docs_to_search = list(self.documents.values())

                results = []
                for doc in docs_to_search:
                    if self._matches(doc, query):
                        results.append(self._project(doc, projection))

                return results

    def __init__(self):
        self.collections: Dict[str, 'DocumentStoreEngine.Collection'] = {}
        self.engine_lock = threading.Lock()

    def get_collection(self, name: str) -> 'DocumentStoreEngine.Collection':
        with self.engine_lock:
            if name not in self.collections:
                self.collections[name] = DocumentStoreEngine.Collection()
            return self.collections[name]

    def insert(self, collection_name: str, doc: Dict[str, Any]) -> str:
        return self.get_collection(collection_name).insert(doc)

    def create_index(self, collection_name: str, field: str):
        self.get_collection(collection_name).create_index(field)

    def find(self, collection_name: str, query: Optional[Dict[str, Any]] = None, projection: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        return self.get_collection(collection_name).find(query, projection)
