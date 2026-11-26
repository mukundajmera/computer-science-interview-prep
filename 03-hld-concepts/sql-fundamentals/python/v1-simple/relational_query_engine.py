import os
import sys
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

class Column:
    def __init__(self, name: str, col_type: type, primary_key: bool = False, unique: bool = False):
        self.name = name
        self.col_type = col_type
        self.primary_key = primary_key
        self.unique = unique

class Table:
    def __init__(self, name: str, columns: List[Column]):
        self.name = name
        self.columns = {col.name: col for col in columns}
        self.rows: List[Dict[str, Any]] = []

        self.primary_keys = [col.name for col in columns if col.primary_key]
        self.unique_columns = [col.name for col in columns if col.unique or col.primary_key]

    def _validate_row(self, row: Dict[str, Any], is_update: bool = False, original_row: Optional[Dict[str, Any]] = None):
        # Type check
        for col_name, value in row.items():
            if col_name in self.columns:
                col = self.columns[col_name]
                if value is not None and not isinstance(value, col.col_type):
                    raise ValueError(f"Column '{col_name}' expects {col.col_type.__name__}, got {type(value).__name__}")

        # Missing primary keys
        if not is_update:
            for pk in self.primary_keys:
                if pk not in row or row[pk] is None:
                    raise ValueError(f"Primary key '{pk}' cannot be null")

        # PK and Unique constraints
        for col_name in self.unique_columns:
            if col_name in row and row[col_name] is not None:
                val = row[col_name]
                for r in self.rows:
                    if is_update and r is original_row:
                        continue
                    if r.get(col_name) == val:
                        raise ValueError(f"Unique constraint failed for column '{col_name}'")

    def insert(self, row: Dict[str, Any]):
        full_row = {col_name: row.get(col_name) for col_name in self.columns}
        self._validate_row(full_row)
        self.rows.append(full_row)

    def update(self, predicate: Callable[[Dict[str, Any]], bool], updates: Dict[str, Any]):
        for r in self.rows:
            if predicate(r):
                new_row = r.copy()
                new_row.update(updates)
                self._validate_row(new_row, is_update=True, original_row=r)
                r.update(updates)

    def delete(self, predicate: Callable[[Dict[str, Any]], bool]):
        self.rows = [r for r in self.rows if not predicate(r)]

    def select(self, predicate: Optional[Callable[[Dict[str, Any]], bool]] = None) -> List[Dict[str, Any]]:
        if predicate is None:
            return [r.copy() for r in self.rows]
        return [r.copy() for r in self.rows if predicate(r)]

class Database:
    def __init__(self):
        self.tables: Dict[str, Table] = {}

    def create_table(self, table: Table):
        self.tables[table.name] = table

    def insert(self, table_name: str, row: Dict[str, Any]):
        self.tables[table_name].insert(row)

    def update(self, table_name: str, predicate: Callable[[Dict[str, Any]], bool], updates: Dict[str, Any]):
        self.tables[table_name].update(predicate, updates)

    def delete(self, table_name: str, predicate: Callable[[Dict[str, Any]], bool]):
        self.tables[table_name].delete(predicate)

    def select(self, table_name: str, predicate: Optional[Callable[[Dict[str, Any]], bool]] = None) -> List[Dict[str, Any]]:
        return self.tables[table_name].select(predicate)

    def inner_join(self, table1_name: str, table2_name: str,
                   join_condition: Callable[[Dict[str, Any], Dict[str, Any]], bool],
                   predicate: Optional[Callable[[Dict[str, Any]], bool]] = None) -> List[Dict[str, Any]]:
        t1 = self.tables[table1_name]
        t2 = self.tables[table2_name]
        result = []
        for r1 in t1.rows:
            for r2 in t2.rows:
                if join_condition(r1, r2):
                    merged = {}
                    for k, v in r1.items():
                        merged[f"{table1_name}.{k}"] = v
                    for k, v in r2.items():
                        merged[f"{table2_name}.{k}"] = v

                    if predicate is None or predicate(merged):
                        result.append(merged)
        return result

    def group_by(self, table_name: str, group_cols: List[str], agg_col: str, agg_func: str) -> List[Dict[str, Any]]:
        t1 = self.tables[table_name]
        groups: Dict[tuple, List[Any]] = {}
        for r in t1.rows:
            key = tuple(r.get(c) for c in group_cols)
            if key not in groups:
                groups[key] = []
            if agg_col in r and r[agg_col] is not None:
                groups[key].append(r[agg_col])

        result = []
        for key, vals in groups.items():
            row = dict(zip(group_cols, key))
            if agg_func == "COUNT":
                row[f"COUNT({agg_col})"] = len(vals)
            elif agg_func == "SUM":
                row[f"SUM({agg_col})"] = sum(vals)
            else:
                raise ValueError(f"Unknown aggregation function {agg_func}")
            result.append(row)
        return result
