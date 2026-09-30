from pydantic import Field
from app.schemas.base import BaseDTO

class VideoJobRequest(BaseDTO):
    query: str = Field(
        ..., 
        description="The topic or question for the generated educational video.", 
        example="What are covalent bonds?",
        min_length=3,
        max_length=200
    )
