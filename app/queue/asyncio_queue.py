import asyncio
from uuid import UUID
from app.queue.interface import BaseQueue

class AsyncioQueue(BaseQueue):
    def __init__(self):
        self._queues = {}

    def _get_queue(self, queue_name: str) -> asyncio.Queue:
        if queue_name not in self._queues:
            self._queues[queue_name] = asyncio.Queue()
        return self._queues[queue_name]

    async def publish(self, queue_name: str, job_id: UUID) -> bool:
        q = self._get_queue(queue_name)
        await q.put(job_id)
        return True

    async def consume(self, queue_name: str, callback: callable) -> None:
        q = self._get_queue(queue_name)
        while True:
            job_id = await q.get()
            try:
                await callback(job_id)
            except Exception as e:
                print(f"Error processing job {job_id}: {e}")
            finally:
                q.task_done()

# Singleton for local testing
local_queue = AsyncioQueue()
