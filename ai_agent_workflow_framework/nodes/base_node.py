from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseNode(ABC):
    node_type = "base"

    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def execute(self, inputs: Dict[str, Any], config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        pass
