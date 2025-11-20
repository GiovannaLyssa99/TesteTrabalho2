from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ChatGenerateRequest(BaseModel):
    query: str

class ChatGenerateResponse(BaseModel):
    answer: str
    latency_ms: Optional[int]

class FileUploadResponse(BaseModel):
    success: bool
    message: str
    doc_id: str
    file_name: str
    uploaded_by: str
    tags: List[str] = []
    insertion_date: datetime

class FileDeleteResponse(BaseModel):
    success: bool
    message: str
    deleted_files: List[str]