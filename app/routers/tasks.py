from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import math

from ..database import get_db
from ..crud import TaskCRUD
from ..schemas import Task, TaskCreate, TaskUpdate, TaskResponse, PaginatedTasks
from ..background import background_processor

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    task: TaskCreate,
    db: AsyncSession = Depends(get_db)
):
    return await TaskCRUD.create_task(db, task)

@router.get("/", response_model=PaginatedTasks)
async def list_tasks(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    title: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    skip = (page - 1) * per_page
    tasks, total = await TaskCRUD.get_tasks(
        db, skip=skip, limit=per_page, title_filter=title, status_filter=status
    )
    
    pages = math.ceil(total / per_page) if total > 0 else 1
    
    return PaginatedTasks(
        items=[TaskResponse.model_validate(task) for task in tasks],
        total=total,
        page=page,
        per_page=per_page,
        pages=pages
    )

@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    task = await TaskCRUD.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    task = await TaskCRUD.update_task(db, task_id, task_update)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.model_validate(task)

@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    success = await TaskCRUD.delete_task(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")

@router.post("/{task_id}/process", status_code=202)
async def start_task_processing(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    task = await TaskCRUD.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task_id in background_processor.running_tasks:
        raise HTTPException(status_code=409, detail="Task is already being processed")
    
    try:
        background_processor.start_background_task(task_id)
        return {"message": f"Background processing started for task {task_id}"}
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))