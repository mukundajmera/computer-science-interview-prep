import threading
from typing import Dict
from logger import Logger
from log_level import LogLevel
from async_processor import AsyncLogProcessor
from appenders import ConsoleAppender

class LoggerFactory:
    _instance = None
    _lock = threading.RLock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(LoggerFactory, cls).__new__(cls)
                cls._instance._init()
            return cls._instance

    def _init(self):
        self._loggers: Dict[str, Logger] = {}
        self._async_processor = AsyncLogProcessor(10000)
        
        self._root_logger = Logger("root", None, self._async_processor)
        self._root_logger.set_level(LogLevel.INFO)
        self._root_logger.add_appender(ConsoleAppender("Console"))
        self._loggers["root"] = self._root_logger

    @classmethod
    def get_instance(cls) -> 'LoggerFactory':
        if cls._instance is None:
            return cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        with cls._lock:
            if cls._instance is not None:
                cls._instance.shutdown()
                cls._instance = None

    def get_logger(self, name: str) -> Logger:
        if not name or name.lower() == "root":
            return self._root_logger

        with self._lock:
            if name not in self._loggers:
                self._loggers[name] = self._create_logger(name)
            return self._loggers[name]

    def _create_logger(self, name: str) -> Logger:
        last_dot_index = name.rfind('.')
        if last_dot_index == -1:
            parent = self._root_logger
        else:
            parent_name = name[:last_dot_index]
            parent = self.get_logger(parent_name)
        return Logger(name, parent, self._async_processor)

    def shutdown(self) -> None:
        if self._async_processor:
            self._async_processor.stop()

