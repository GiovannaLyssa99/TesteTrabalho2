from typing import Optional
from app.modules.agent_chat.schemas import ListaMsgResponse, ListaConversaResponse, CreateConversaResponse, MessageInput
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.database import get_db
from app.infra.dependency_provider import get_chat_service, get_bd_vetorial_service
from app.modules.auth.auth import get_current_user
from app.modules.usuarios.models import User

chat_agent_router = APIRouter(prefix="/chat", tags=["chat"])

# Endpoints para Conversas

conversas_router = APIRouter(prefix="/conversas", tags=["Conversas"])

@conversas_router.post("", response_model=CreateConversaResponse)
async def iniciar_conversa(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db), service = Depends(get_chat_service)):
    
    """
    Essa é a rota para criação de novas conversas.
    """
    try:
        user_id = current_user.id
        return await service.iniciar_conversa(user_id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@conversas_router.get("", response_model=list[ListaConversaResponse])
async def buscar_conversas(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db), service = Depends(get_chat_service)):
    
    """
    Essa é a rota para buscar conversas de um usuário.
    """
    try:
        user_id = current_user.id
        return await service.listar_conversas_usuario(user_id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# Endpoints para Mensagens

messages_router = APIRouter(prefix="/messages", tags=["Messages"])

@messages_router.post("/send", dependencies=[Depends(get_current_user)])
async def send_message(msg: MessageInput, db: AsyncSession = Depends(get_db), service = Depends(get_chat_service)):
    """
    Essa é a rota para envio de mensagens do usuário para o sistema de chat.
    """
    try:
        result = await service.send_message(msg, db)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return result


@messages_router.get("/history", response_model=list[ListaMsgResponse], dependencies=[Depends(get_current_user)])
async def get_history(thread_id:str, db: AsyncSession = Depends(get_db), service = Depends(get_chat_service)):
    """
    Essa é a buscar histórico de mensagens de uma determinada conversa.
    """
    try:
        result = await service.listar_historico_mensagens(thread_id, db)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return result


chat_agent_router.include_router(conversas_router)
chat_agent_router.include_router(messages_router)
