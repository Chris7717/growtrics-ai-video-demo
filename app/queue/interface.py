from abc import ABC, abstractmethod
from uuid import UUID

class BaseQueue(ABC):
    @abstractmethod
    async def publish(self, queue_name: str, job_id: UUID) -> bool:
        pass

    @abstractmethod
    async def consume(self, queue_name: str, callback: callable) -> None:
        pass
