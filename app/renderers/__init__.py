from app.renderers.registry import registry
from app.renderers.title_card import TitleCardRenderer

registry.register("title_card", TitleCardRenderer)
# More renderers can be registered here as needed
