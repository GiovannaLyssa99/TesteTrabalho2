from uuid import UUID
from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime

# Schemas para endpoints de chat

class CreateConversaResponse(BaseModel):
    thread_id: str
    user_id: Optional[int] = None

class ListaConversaResponse(BaseModel):
    thread_id: UUID
    user_id: int
    titulo: str

    class Config:
        orm_mode = True 

class ListaMsgResponse(BaseModel):
    content: str
    type: str

class MessageInput(BaseModel):
    thread_id: str
    content: str | dict