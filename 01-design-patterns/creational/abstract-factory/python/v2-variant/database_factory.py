"""v2-variant: Abstract Factory Pattern for Cross-Platform Database Ecosystems.

Encapsulates dialect-specific connection, command, and transaction behaviors within
coherent provider families (Postgres vs MySQL).
"""
from abc import ABC, abstractmethod


class DbConnection(ABC):
    @abstractmethod
    def open(self) -> None:
        pass

    @abstractmethod
    def is_open(self) -> bool:
        pass

    @abstractmethod
    def get_dialect(self) -> str:
        pass


class DbCommand(ABC):
    @abstractmethod
    def execute(self, sql: str) -> str:
        pass


class DbTransaction(ABC):
    @abstractmethod
    def begin(self) -> None:
        pass

    @abstractmethod
    def commit(self) -> None:
        pass

    @abstractmethod
    def rollback(self) -> None:
        pass

    @abstractmethod
    def is_active(self) -> bool:
        pass


class DatabaseFactory(ABC):
    @abstractmethod
    def create_connection(self) -> DbConnection:
        pass

    @abstractmethod
    def create_command(self) -> DbCommand:
        pass

    @abstractmethod
    def create_transaction(self) -> DbTransaction:
        pass


# --- PostgreSQL Family ---

class PostgresConnection(DbConnection):
    def __init__(self) -> None:
        self._open = False

    def open(self) -> None:
        self._open = True

    def is_open(self) -> bool:
        return self._open

    def get_dialect(self) -> str:
        return "POSTGRESQL"


class PostgresCommand(DbCommand):
    def execute(self, sql: str) -> str:
        return f"[PostgreSQL Executed]: {sql}"


class PostgresTransaction(DbTransaction):
    def __init__(self) -> None:
        self._active = False

    def begin(self) -> None:
        self._active = True

    def commit(self) -> None:
        self._active = False

    def rollback(self) -> None:
        self._active = False

    def is_active(self) -> bool:
        return self._active


class PostgresFactory(DatabaseFactory):
    def create_connection(self) -> DbConnection:
        return PostgresConnection()

    def create_command(self) -> DbCommand:
        return PostgresCommand()

    def create_transaction(self) -> DbTransaction:
        return PostgresTransaction()


# --- MySQL Family ---

class MySqlConnection(DbConnection):
    def __init__(self) -> None:
        self._open = False

    def open(self) -> None:
        self._open = True

    def is_open(self) -> bool:
        return self._open

    def get_dialect(self) -> str:
        return "MYSQL"


class MySqlCommand(DbCommand):
    def execute(self, sql: str) -> str:
        return f"[MySQL Executed]: {sql}"


class MySqlTransaction(DbTransaction):
    def __init__(self) -> None:
        self._active = False

    def begin(self) -> None:
        self._active = True

    def commit(self) -> None:
        self._active = False

    def rollback(self) -> None:
        self._active = False

    def is_active(self) -> bool:
        return self._active


class MySqlFactory(DatabaseFactory):
    def create_connection(self) -> DbConnection:
        return MySqlConnection()

    def create_command(self) -> DbCommand:
        return MySqlCommand()

    def create_transaction(self) -> DbTransaction:
        return MySqlTransaction()
