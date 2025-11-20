import asyncio
import uuid
from fastapi import HTTPException
from app.modules.agent_chat.models import Conversa, Mensagem, MessageType
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
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
        
    async def iniciar_conversa(self, user_id: int | None, db: AsyncSession):
        try:
            conversa = Conversa(user_id=user_id)
            db.add(conversa)
            await db.commit()
            await db.refresh(conversa)
        except Exception as e:
            await db.rollback()
            print(f"Erro ao criar conversa no postgres: {e}")
            raise

        return {"thread_id": str(conversa.thread_id), "user_id": conversa.user_id}
    
    async def excluir_conversa(self, thread_id: str, db: AsyncSession):
        try:
            result = await db.execute(select(Conversa).where(Conversa.thread_id == thread_id))
            conversa = result.scalar_one_or_none()

            if not conversa:
                raise HTTPException(status_code=404, detail="Conversa não encontrada")

            await db.delete(conversa)
            await db.commit()
        except Exception as e:
            await db.rollback()
            print(f"Erro ao excluir conversa no postgres - thread_id = {thread_id}: {e}")
            raise

    async def salvar_mensagem(self, content: str, type: str, thread_id: str, db: AsyncSession):
        try:
            msg = Mensagem(content=content, type=type, conversa_id=thread_id)
            db.add(msg)
            await db.commit()
        except Exception as e:
            await db.rollback()
            print(f"Erro ao salvar mensagem no postgres - thread_id = {thread_id}: {e}")
            raise


    async def send_message(self, msg: MessageInput, db: AsyncSession):
        conversa = await db.scalar(select(Conversa).where(Conversa.thread_id == msg.thread_id))
        print("thread coletada")

        if not conversa:
            raise HTTPException(status_code=404, detail="Conversa/thread não encontrada")

        await self.salvar_mensagem(content=msg.content, type=MessageType.HUMAN, thread_id=conversa.thread_id, db=db)

        result = await graph.ainvoke(
            {"messages": [HumanMessage(msg.content, name="query")]},
            context={"user_id": conversa.user_id},
            config={"configurable": {"thread_id": conversa.thread_id}},
        )

        print(result)

        answer = None
        for m in reversed(result["messages"]):
            if m.content and isinstance(m, AIMessage) and not m.response_metadata.get("__is_handoff_back"):
                answer = m.content
                break

        print("answer:" + str(answer))
        await self.salvar_mensagem(content=answer, type=MessageType.AI, thread_id=conversa.thread_id, db=db)

        return {
            "thread_id": conversa.thread_id,
            "user_message": msg.content,
            "assistant_message": answer,
        }
    
        
    async def listar_conversas_usuario(self, user_id: int, db: AsyncSession):
        try:
            result = await db.execute(select(Conversa).where(Conversa.user_id == user_id))
            conversas = result.scalars().all()

            if not conversas:
                return []
                #raise HTTPException(status_code=404, detail="Usuário não possui conversas")

            for conversa in conversas:
                if not conversa.titulo or conversa.titulo.strip() == "":
                    result_msgs = await db.execute(
                        select(Mensagem.content)
                        .where(Mensagem.conversa_id == conversa.thread_id)
                        .order_by(Mensagem.id.asc())
                        .limit(10)
                    )
                    primeiras_msgs = result_msgs.all()

                    if not primeiras_msgs:
                        await self.excluir_conversa(conversa.thread_id, db)
                        conversas.remove(conversa)
                        continue

                    texts = "\n".join([m[0] for m in primeiras_msgs])

                    if texts.strip():
                        prompt = (
                            f"Analise as mensagens a seguir e retorne um título para ser aplicado à essa conversa que represente o que está sendo discutido. "
                            f"O título deve ser uma frase concisa. Mensagens: {texts}"
                        )
                        try:
                            titulo_gerado = await llm.ainvoke(input=prompt)
                            conversa.titulo = titulo_gerado.content
                            db.add(conversa)
                        except Exception as e:
                            print(f"Erro ao gerar título para conversa {conversa.thread_id}: {e}")
                            await db.rollback()
                            continue

            await db.commit()
        except Exception as e:
            print(f"Erro ao buscar conversas - user_id = {user_id}: {e}")
            raise

        return conversas
    
    async def listar_historico_mensagens(self, thread_id: str, db: AsyncSession):
        try:
            result = await db.execute(
                select(Mensagem.content, Mensagem.type).where(Mensagem.conversa_id == thread_id)
            )
            mensagens = result.all()

            if not mensagens:
                raise HTTPException(status_code=404, detail="Mensagens não encontradas para essa thread_id/conversa")
        except Exception as e:
            print(f"Erro ao buscar mensagens - thread_id = {thread_id}: {e}")
            raise

        return [{"content": c, "type": t} for c, t in mensagens]