from pydantic import BaseModel, Field, AliasChoices
from typing import Optional, List
from enum import Enum

class ProcessingMode(str, Enum):
    TASK_ONLY = "task_only"
    CLIENT_REPLY_ONLY = "reply_only"
    THREAD_SUMMARY = "thread_summary"
    FULL_ASSISTANT = "full_assistant"

class VisibleMessage(BaseModel):
    author: str
    date: str
    text: str

class CRMContext(BaseModel):
    branch_id: str = Field(..., description="ID ветки из H1, например 818051")
    h1_title: str = Field(..., description="Полный заголовок H1 для извлечения домена")

class DraftRequest(BaseModel):
    mode: ProcessingMode
    context: CRMContext
    messages: List[VisibleMessage]

class TaskStatus(BaseModel):
    task_name: str = Field(..., validation_alias=AliasChoices('task_name', 'task'))
    status: str

class DraftResponse(BaseModel):
    task_name: Optional[str] = None
    task_description: Optional[str] = None
    task_time_minutes: Optional[int] = None
    task_executor: Optional[str] = None
    email_reply_text: Optional[str] = None
    thread_summary: Optional[str] = None
    parsed_tasks_statuses: Optional[List[TaskStatus]] = None