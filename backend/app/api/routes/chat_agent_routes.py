from typing import Optional
from app.modules.agent_chat.schemas import ListaMsgResponse, ListaConversaResponse, CreateConversaResponse, MessageInput
import time
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.infra.database import SessionLocal, get_db
from app.infra.dependency_provider import get_chat_service, get_bd_vetorial_service

chat_agent_router = APIRouter(prefix="/chat", tags=["chat"])

# Endpoints para Conversas

conversas_router = APIRouter(prefix="/conversas", tags=["Conversas"])

@conversas_router.post("", response_model=CreateConversaResponse)
async def iniciar_conversa(user_id: Optional[int] = Query(None), db: Session = Depends(get_db), service = Depends(get_chat_service)):
    
    """
    Essa é a rota para criação de novas conversas.
    """
    try:
        return service.iniciar_conversa(user_id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@conversas_router.get("", response_model=list[ListaConversaResponse])
async def buscar_conversas(user_id: int, db: Session = Depends(get_db), service = Depends(get_chat_service)):
    
    """
    Essa é a rota para buscar conversas de um usuário.
    """
    try:
        return service.listar_conversas_usuario(user_id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@conversas_router.post("logout")
async def logout(thread_id:str, user_id: Optional[int] = Query(None), db: Session = Depends(get_db), service = Depends(get_chat_service)):
    
    """
    Essa é a rota deve ser usada no encerramento de sessões de usuário.
    Ela exclui dados de conversas caso a sessão seja anônima.

    ATENÇÃO: Ainda não está excluindo checkpoints, apenas conversas.
    """
    try:
        if not user_id:
            service.excluir_conversa_anonima(thread_id, db)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return {"status": "sessão encerrada"}


# Endpoints para Mensagens

messages_router = APIRouter(prefix="/messages", tags=["Messages"])

@messages_router.post("/send")
async def send_message(msg: MessageInput, db: Session = Depends(get_db), service = Depends(get_chat_service)):
    """
    Essa é a rota para envio de mensagens do usuário para o sistema de chat.
    """
    try:
        result = await service.send_message(msg, db)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return result


@messages_router.get("/history", response_model=list[ListaMsgResponse])
async def get_history(thread_id:str, db: Session = Depends(get_db), service = Depends(get_chat_service)):
    """
    Essa é a buscar histórico de mensagens de uma determinada conversa.
    """
    try:
        result = service.listar_historico_mensagens(thread_id, db)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return result


chat_agent_router.include_router(conversas_router)
chat_agent_router.include_router(messages_router)
