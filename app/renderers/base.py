from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseRenderer(ABC):
    @abstractmethod
    async def render(self, visual_data: Dict[str, Any], duration: float, output_path: str) -> bool:
        """
        Render a visual scene.
        Returns True on success, False otherwise.
        """
        pass
