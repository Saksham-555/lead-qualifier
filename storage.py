import json
import threading
from abc import ABC, abstractmethod


class ResultSink(ABC):
    @abstractmethod
    def save(self, record: dict) -> None: ...


class JsonlSink(ResultSink):
    def __init__(self, path: str = "results.jsonl"):
        self.path = path
        self._lock = threading.Lock()

    def save(self, record: dict) -> None:
        with self._lock, open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
