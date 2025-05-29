from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), nullable=False, default="pending")
    priority = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    logs = relationship("TaskLog", back_populates="task", cascade="all, delete-orphan")

class TaskLog(Base):
    __tablename__ = "task_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    status = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    task = relationship("Task", back_populates="logs")