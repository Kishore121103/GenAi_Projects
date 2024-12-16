from abc import ABC, abstractmethod
from typing import List, Dict

class AgentProtocol(ABC):
    @abstractmethod
    def get_response(self, messages: List[Dict[str, str]]) -> Dict[str, str]:
        """
        Abstract method to ensure all agents implement this interface.
        """
        pass
