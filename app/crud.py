from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List
from . import models, schemas

class TaskCRUD:
    @staticmethod
    async def create_task(db: AsyncSession, task: schemas.TaskCreate) -> models.Task:
        db_task = models.Task(**task.model_dump())
        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)
        
        log = models.TaskLog(task_id=db_task.id, status=db_task.status)
        db.add(log)
        await db.commit()
        
        return db_task
    
    @staticmethod
    async def get_task(db: AsyncSession, task_id: int) -> Optional[models.Task]:
        result = await db.execute(
            select(models.Task)
            .options(selectinload(models.Task.logs))
            .where(models.Task.id == task_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_tasks(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        title_filter: Optional[str] = None,
        status_filter: Optional[str] = None
    ) -> tuple[List[models.Task], int]:
        query = select(models.Task)
        count_query = select(func.count(models.Task.id))
        
        if title_filter:
            filter_condition = models.Task.title.ilike(f"%{title_filter}%")
            query = query.where(filter_condition)
            count_query = count_query.where(filter_condition)
        
        if status_filter:
            status_condition = models.Task.status == status_filter
            query = query.where(status_condition)
            count_query = count_query.where(status_condition)
        
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        query = query.offset(skip).limit(limit).order_by(models.Task.created_at.desc())
        result = await db.execute(query)
        tasks = result.scalars().all()
        
        return tasks, total
    
    @staticmethod
    async def update_task(
        db: AsyncSession, 
        task_id: int, 
        task_update: schemas.TaskUpdate
    ) -> Optional[models.Task]:
        result = await db.execute(select(models.Task).where(models.Task.id == task_id))
        db_task = result.scalar_one_or_none()
        
        if not db_task:
            return None
        
        update_data = task_update.model_dump(exclude_unset=True)
        old_status = db_task.status
        
        for field, value in update_data.items():
            setattr(db_task, field, value)
        
        await db.commit()
        await db.refresh(db_task)
        
        if "status" in update_data and old_status != db_task.status:
            log = models.TaskLog(task_id=db_task.id, status=db_task.status)
            db.add(log)
            await db.commit()
        
        return db_task
    
    @staticmethod
    async def delete_task(db: AsyncSession, task_id: int) -> bool:
        result = await db.execute(select(models.Task).where(models.Task.id == task_id))
        db_task = result.scalar_one_or_none()
        
        if not db_task:
            return False
        
        await db.delete(db_task)
        await db.commit()
        return True