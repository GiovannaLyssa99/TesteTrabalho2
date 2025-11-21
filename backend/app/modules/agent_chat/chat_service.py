import asyncio
import uuid
from fastapi import HTTPException
from app.modules.agent_chat.models import Conversa, Mensagem, MessageType
from sqlalchemy.orm import Session
from app.modules.agent_chat.schemas import MessageInput
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import Command
from langgraph.checkpoint.postgres import PostgresSaver
from app.infra.database import get_db_connection, get_db
from app.infra.config import Config
from app.modules.agent_chat.V2_multiagent.graph_workflow import graph
from app.modules.agent_chat.llm import llm

class ChatAgentService:

    def __init__(self, graph):
        self.graph = graph
        
    def iniciar_conversa(self, user_id: int | None, db: Session):

        try:
            conversa = Conversa(user_id=user_id)
            db.add(conversa)
            db.commit()
            db.refresh(conversa)
        
        except Exception as e:
            db.rollback()
            print(f"Erro ao criar conversa no postgres: {e}")
            raise

        return {"thread_id": str(conversa.thread_id), "user_id": conversa.user_id}
    
    def excluir_conversa_anonima(self, thread_id: str, db: Session):

        try:
            conversa = db.query(Conversa).filter_by(thread_id=thread_id).first()

            if not conversa:
                raise HTTPException(status_code=404, detail="Conversa não encontrada")

            if conversa.user_id:
                raise HTTPException(status_code=400, detail="Conversa não é anônima")

            # try:
            #     await asyncio.to_thread(self.graph.checkpointer.delete_thread, uuid.UUID(thread_id))
            # except Exception as e:
            #     print(f"Erro ao excluir no checkpointer: {e}")

            db.delete(conversa)
            db.commit()

        except Exception as e:
            db.rollback()
            print(f"Erro ao excluir conversa no postgres - thread_id = {thread_id}: {e}")
            raise

    def salvar_mensagem(self, content: str, type: str, thread_id: str, db: Session):

        try:
            msg = Mensagem(content=content, type=type, conversa_id=thread_id)
            db.add(msg)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Erro ao salvar mensagem no postgres - thread_id = {thread_id}: {e}")
            raise

    async def send_message(self, msg: MessageInput, db: Session):

        conversa = db.query(Conversa).filter_by(thread_id=msg.thread_id).first()

        print("thread coletada")

        if not conversa:
            raise HTTPException(status_code=404, detail="Conversa/thread não encontrada")

        if msg.user_id and conversa.user_id and conversa.user_id != msg.user_id:
            raise HTTPException(status_code=403, detail="Conversa/thread pertence a outro usuário")
        
        self.salvar_mensagem(content=msg.content, type=MessageType.HUMAN, thread_id=conversa.thread_id, db=db)
        
        result = await graph.ainvoke({"messages": [HumanMessage(msg.content, name="query")]},
                                    context={"user_id": msg.user_id},
                                    config={"configurable": {"thread_id": conversa.thread_id}})

        print(result)
        
        answer: str
        for m in reversed(result["messages"]): 
            if m.content and isinstance(m, AIMessage) and not m.response_metadata.get("__is_handoff_back"):
                answer = m.content
                break

        print("answer:" + answer)
        self.salvar_mensagem(content=answer, type=MessageType.AI, thread_id=conversa.thread_id, db=db)

        return {
            "thread_id": conversa.thread_id,
            "user_message": msg.content,
            "assistant_message": answer
        }
    
        
    def listar_conversas_usuario(self, user_id: int, db: Session):
        try:
            conversas = db.query(Conversa).filter_by(user_id=user_id).all()

            if not conversas:
                raise HTTPException(status_code=404, detail="Usuário não possui conversas")
            
            for conversa in conversas:
                if not conversa.titulo or conversa.titulo.strip() == "":
                    primeiras_msgs = (
                        db.query(Mensagem.content)
                        .filter(Mensagem.conversa_id == conversa.thread_id)
                        .order_by(Mensagem.id.asc())
                        .limit(10)
                        .all()
                    )
                    texts = "\n".join([m[0] for m in primeiras_msgs])

                    if texts:
                        prompt = (
                            f"Analise as mensagens a seguir e retorne um título para ser aplicado à essa conversa que represente o que está sendo discutido. "
                            f"O título deve ser uma frase concisa. Mensagens: {texts}"
                        )
                        titulo_gerado = llm.invoke(input=prompt)
                        conversa.titulo = titulo_gerado.content
                        db.add(conversa)

            db.commit() 
            
        except Exception as e:
            print(f"Erro ao buscar conversas - user_id = {user_id}: {e}")
            raise
        
        return conversas
    
    def listar_historico_mensagens(self, thread_id:str, db: Session):
        try:
            mensagens = db.query(Mensagem.content, Mensagem.type).filter(Mensagem.conversa_id == thread_id).all()

            if not mensagens:
                raise HTTPException(status_code=404, detail="Mensagens não encontradas para essa thread_id/conversa")
            
        except Exception as e:
            print(f"Erro ao buscar mensagens - thread_id = {thread_id}: {e}")
            raise

        return [{"content": c, "type": t} for c, t in mensagens]