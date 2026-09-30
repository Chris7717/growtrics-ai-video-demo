from typing import TypeVar, Generic, Type, Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import DeclarativeBase
from pydantic import BaseModel

ModelType = TypeVar("ModelType", bound=DeclarativeBase)
CreateDTOType = TypeVar("CreateDTOType", bound=BaseModel)
UpdateDTOType = TypeVar("UpdateDTOType", bound=BaseModel)

class BaseRepository(Generic[ModelType, CreateDTOType, UpdateDTOType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, session: AsyncSession, id: Any) -> Optional[ModelType]:
        result = await session.execute(select(self.model).where(self.model.id == id))
        return result.scalars().first()

    async def get_multi(self, session: AsyncSession, skip: int = 0, limit: int = 100) -> List[ModelType]:
        result = await session.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, session: AsyncSession, obj_in: CreateDTOType) -> ModelType:
        # Rule 4: Use DTO unpacking
        db_obj = self.model(**obj_in.model_dump())
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(self, session: AsyncSession, db_obj: ModelType, obj_in: UpdateDTOType | dict) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
            
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def delete(self, session: AsyncSession, id: Any) -> bool:
        obj = await self.get(session, id)
        if obj:
            await session.delete(obj)
            await session.commit()
            return True
        return False
