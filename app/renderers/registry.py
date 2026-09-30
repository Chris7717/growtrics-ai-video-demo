from typing import Type, Dict
from app.renderers.base import BaseRenderer

class RendererRegistry:
    def __init__(self):
        self._renderers: Dict[str, Type[BaseRenderer]] = {}

    def register(self, visual_type: str, renderer_class: Type[BaseRenderer]):
        self._renderers[visual_type] = renderer_class

    def get(self, visual_type: str) -> Type[BaseRenderer]:
        return self._renderers.get(visual_type)

registry = RendererRegistry()
