from pydantic import BaseModel, ConfigDict

class BaseDTO(BaseModel):
    """
    Base class for all DTOs (Data Transfer Objects).
    - `from_attributes=True`: Allows parsing data from SQLAlchemy models.
    """
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
