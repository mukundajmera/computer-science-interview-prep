"""v3-advanced: Type-Safe Staged Builder with Runtime Invariant Validation.

Uses compile-time interface staging and runtime checks to enforce mandatory clauses
(SELECT -> FROM) before optional clauses (WHERE, LIMIT) on SqlQuery.
"""
from typing import List, Optional, Tuple


class SqlQuery:
    """Immutable SQL query constructed via staged validation."""

    def __init__(self, columns: List[str], table: str, where_clause: Optional[str] = None, limit: Optional[int] = None) -> None:
        self.columns: Tuple[str, ...] = tuple(columns)
        self.table: str = table
        self.where_clause: Optional[str] = where_clause
        self.limit: Optional[int] = limit

    def to_sql(self) -> str:
        sql = f"SELECT {', '.join(self.columns)} FROM {self.table}"
        if self.where_clause:
            sql += f" WHERE {self.where_clause.strip()}"
        if self.limit is not None:
            sql += f" LIMIT {self.limit}"
        return sql


class _BuilderStage:
    def __init__(self, columns: List[str], table: str, where_clause: Optional[str] = None, limit: Optional[int] = None) -> None:
        self._columns = columns
        self._table = table
        self._where_clause = where_clause
        self._limit = limit

    def where(self, condition: str) -> "_BuilderStage":
        if condition and condition.strip():
            self._where_clause = condition.strip()
        return self

    def limit(self, limit_val: int) -> "_BuilderStage":
        if limit_val <= 0:
            raise ValueError(f"Limit must be positive: {limit_val}")
        self._limit = limit_val
        return self

    def build(self) -> SqlQuery:
        if not self._columns:
            raise ValueError("Columns cannot be empty")
        if not self._table:
            raise ValueError("Table cannot be empty")
        return SqlQuery(self._columns, self._table, self._where_clause, self._limit)


class _FromStage:
    def __init__(self, columns: List[str]) -> None:
        self._columns = columns

    def from_table(self, table: str) -> _BuilderStage:
        if not table or not table.strip():
            raise ValueError("Table name cannot be blank")
        return _BuilderStage(self._columns, table.strip())


class StagedQueryBuilder:
    """Entry point for staged query construction."""

    @staticmethod
    def select(*columns: str) -> _FromStage:
        if not columns:
            raise ValueError("At least one column must be specified")
        clean_cols = [c.strip() for c in columns if c and c.strip()]
        if not clean_cols:
            raise ValueError("Column names cannot be blank")
        return _FromStage(clean_cols)
