import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from .database import async_session_maker
from .crud import TaskCRUD
from .schemas import TaskUpdate, TaskStatus

class BackgroundTaskProcessor:
    def __init__(self):
        self.running_tasks = set()
    
    async def process_task(self, task_id: int):
        if task_id in self.running_tasks:
            raise ValueError(f"Task {task_id} is already being processed")
        
        self.running_tasks.add(task_id)
        
        try:
            async with async_session_maker() as db:
                await TaskCRUD.update_task(
                    db, task_id, TaskUpdate(status=TaskStatus.IN_PROGRESS)
                )
                
                print(f"Processing task {task_id}")
                await asyncio.sleep(5)
                
                await TaskCRUD.update_task(
                    db, task_id, TaskUpdate(status=TaskStatus.COMPLETED)
                )
                
                print(f"Task {task_id} completed successfully")
                
        except Exception as e:
            print(f"Error processing task {task_id}: {e}")
            async with async_session_maker() as db:
                await TaskCRUD.update_task(
                    db, task_id, TaskUpdate(status=TaskStatus.PENDING)
                )
        finally:
            self.running_tasks.discard(task_id)
    
    def start_background_task(self, task_id: int):
        task = asyncio.create_task(self.process_task(task_id))
        return task

background_processor = BackgroundTaskProcessor()